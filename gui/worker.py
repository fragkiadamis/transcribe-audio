from PySide6.QtCore import QThread, Signal

from core.transcriber import Transcriber
from core.translator import Translator
from core.writer import FORMATS, OutputWriter


class TranscribeWorker(QThread):
    progress = Signal(str, int, int)  # stage, advance, total
    finished = Signal(str)            # output directory
    error = Signal(str)

    def __init__(self, audio_path, model, device, lang, prompt, translate_to, translator_backend, api_key):
        super().__init__()
        self.audio_path = audio_path
        self.model = model
        self.device = device
        self.lang = lang or None
        self.prompt = prompt or None
        self.translate_to = translate_to or None
        self.translator_backend = translator_backend
        self.api_key = api_key or None

    def run(self):
        try:
            transcriber = Transcriber(model_name=self.model, device=self.device)
            translator = Translator(backend=self.translator_backend, target=self.translate_to, api_key=self.api_key)
            writer = OutputWriter(audio_path=self.audio_path)

            self.progress.emit("load", 0, 0)
            transcriber.load()
            self.progress.emit("load", 1, 1)

            self.progress.emit("transcribe", 0, 0)
            result = transcriber.transcribe(self.audio_path, lang=self.lang, prompt=self.prompt)
            self.progress.emit("transcribe", 1, 1)

            source_lang = result.get("language") or self.lang
            if self.translate_to and self.translate_to != source_lang:
                total = len(result["segments"])
                self.progress.emit("translate", 0, total)

                def on_translate(advance=1, total=None):
                    self.progress.emit("translate", advance, 0)

                result = translator.translate(result, on_progress=on_translate)
            self.progress.emit("translate_done", 0, 0)

            total_formats = len(FORMATS)
            self.progress.emit("save", 0, total_formats)

            def on_save(advance=1, total=None):
                self.progress.emit("save", advance, 0)

            out_dir = writer.write(result, on_progress=on_save)
            self.finished.emit(str(out_dir))

        except ValueError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")
