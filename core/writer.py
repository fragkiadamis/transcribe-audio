from pathlib import Path

from whisper.utils import get_writer

FORMATS = ("json", "srt", "tsv", "vtt", "txt")


class OutputWriter:
    def __init__(self, audio_path, output_dir="output"):
        self.audio_path = audio_path
        self.out_dir = Path(output_dir) / Path(audio_path).stem

    def write(self, result, on_progress=None):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        for fmt in FORMATS:
            writer = get_writer(fmt, str(self.out_dir))
            writer(result, self.audio_path, {})
            if on_progress:
                on_progress(advance=1)
        return self.out_dir
