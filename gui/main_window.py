from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.translator import TRANSLATORS
from gui.worker import TranscribeWorker

MODELS = ["tiny", "base", "small", "medium", "large"]
DEVICES = ["auto", "cpu", "cuda"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcribe Audio")
        self.setMinimumWidth(620)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addWidget(self._build_audio_section())
        layout.addWidget(self._build_settings_section())
        layout.addWidget(self._build_translation_section())
        layout.addWidget(self._build_run_section())
        layout.addStretch()

    # ── Sections ─────────────────────────────────────────────────────────────

    def _build_audio_section(self):
        group = QGroupBox("Audio File")
        layout = QHBoxLayout(group)

        self.audio_path_input = QLineEdit()
        self.audio_path_input.setPlaceholderText("Select an audio file…")
        self.audio_path_input.setReadOnly(True)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._on_browse)

        layout.addWidget(self.audio_path_input)
        layout.addWidget(browse_btn)
        return group

    def _build_settings_section(self):
        group = QGroupBox("Settings")
        layout = QFormLayout(group)

        self.lang_input = QLineEdit()
        self.lang_input.setPlaceholderText("Auto-detect")
        self.lang_input.setMaxLength(2)
        self.lang_input.setFixedWidth(80)

        self.model_combo = QComboBox()
        self.model_combo.addItems(MODELS)
        self.model_combo.setCurrentText("base")
        self.model_combo.setFixedWidth(120)

        self.device_combo = QComboBox()
        self.device_combo.addItems(DEVICES)
        self.device_combo.setFixedWidth(120)

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Optional — guide transcription style or vocabulary")

        layout.addRow("Language:", self.lang_input)
        layout.addRow("Model:", self.model_combo)
        layout.addRow("Device:", self.device_combo)
        layout.addRow("Prompt:", self.prompt_input)
        return group

    def _build_translation_section(self):
        group = QGroupBox("Translation")
        layout = QFormLayout(group)

        self.translate_to_input = QLineEdit()
        self.translate_to_input.setPlaceholderText("e.g. en, fr, el — leave empty to skip")
        self.translate_to_input.setFixedWidth(200)

        self.translator_combo = QComboBox()
        self.translator_combo.addItems(list(TRANSLATORS.keys()))
        self.translator_combo.setFixedWidth(160)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Required for deepl, microsoft, yandex…")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Translate to:", self.translate_to_input)
        layout.addRow("Backend:", self.translator_combo)
        layout.addRow("API Key:", self.api_key_input)
        return group

    def _build_run_section(self):
        group = QGroupBox("Run")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        self.transcribe_btn = QPushButton("Transcribe")
        self.transcribe_btn.setFixedHeight(36)
        self.transcribe_btn.clicked.connect(self._on_transcribe)

        self.progress_load = self._make_progress_row("Loading model")
        self.progress_transcribe = self._make_progress_row("Transcribing")
        self.progress_translate = self._make_progress_row("Translating")
        self.progress_save = self._make_progress_row("Saving output")

        self.output_label = QLabel()
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_label.hide()

        layout.addWidget(self.transcribe_btn)
        for row in [self.progress_load, self.progress_transcribe,
                    self.progress_translate, self.progress_save]:
            layout.addWidget(row)
            row.hide()
        layout.addWidget(self.output_label)
        return group

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_progress_row(self, label_text):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(f"{label_text}…")
        label.setFixedWidth(140)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)

        layout.addWidget(label)
        layout.addWidget(bar)

        row.label = label
        row.bar = bar
        return row

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.aac);;All Files (*)",
        )
        if path:
            self.audio_path_input.setText(path)

    def _on_transcribe(self):
        audio_path = self.audio_path_input.text().strip()
        if not audio_path:
            QMessageBox.warning(self, "No file selected", "Please select an audio file first.")
            return

        self.transcribe_btn.setEnabled(False)
        self.output_label.hide()

        for row in [self.progress_load, self.progress_transcribe,
                    self.progress_translate, self.progress_save]:
            row.bar.setValue(0)
            row.show()

        self._worker = TranscribeWorker(
            audio_path=audio_path,
            model=self.model_combo.currentText(),
            device=self.device_combo.currentText(),
            lang=self.lang_input.text().strip() or None,
            prompt=self.prompt_input.text().strip() or None,
            translate_to=self.translate_to_input.text().strip() or None,
            translator_backend=self.translator_combo.currentText(),
            api_key=self.api_key_input.text().strip() or None,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, stage, advance, total):
        stage_map = {
            "load": self.progress_load,
            "transcribe": self.progress_transcribe,
            "translate": self.progress_translate,
            "save": self.progress_save,
        }
        row = stage_map.get(stage)
        if row is None:
            return
        bar = row.bar
        if total > 0:
            bar.setRange(0, total)
            bar.setValue(0)
        elif advance > 0:
            if bar.maximum() == 0:
                bar.setRange(0, 1)
            bar.setValue(bar.value() + advance)

    def _on_finished(self, out_dir):
        self.progress_load.bar.setValue(self.progress_load.bar.maximum() or 1)
        self.progress_transcribe.bar.setValue(self.progress_transcribe.bar.maximum() or 1)
        self.progress_save.bar.setValue(self.progress_save.bar.maximum() or 1)

        self.output_label.setText(f"Saved to {out_dir}/")
        self.output_label.show()
        self.transcribe_btn.setEnabled(True)

    def _on_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.transcribe_btn.setEnabled(True)
