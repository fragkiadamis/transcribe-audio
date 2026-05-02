import argparse
from pathlib import Path

import whisper
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from whisper.utils import get_writer

FORMATS = ("json", "srt", "tsv", "vtt", "txt")


def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Whisper")
    parser.add_argument("audio", help="Path to the audio file")
    parser.add_argument("-l", "--lang", help="2-letter language code (e.g. en, fr, ar, el)")
    parser.add_argument("-m", "--model", default="base", choices=["tiny", "base", "small", "medium", "large"], help="Whisper model to use (default: base)")
    parser.add_argument("-p", "--prompt", help="Initial prompt to guide transcription style or vocabulary")
    args = parser.parse_args()

    if args.lang is not None and len(args.lang) != 2:
        parser.error("Language code must be exactly 2 letters")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
    ) as progress:
        load_task = progress.add_task("Loading model...", total=None)
        model = whisper.load_model(args.model)
        progress.update(load_task, completed=True, total=1, description="Model loaded")

        transcribe_kwargs = {}
        if args.lang:
            transcribe_kwargs["language"] = args.lang
        if args.prompt:
            transcribe_kwargs["initial_prompt"] = args.prompt

        transcribe_task = progress.add_task("Transcribing...", total=None)
        result = model.transcribe(args.audio, verbose=None, **transcribe_kwargs)
        progress.update(transcribe_task, completed=True, total=1, description="Transcription done")

        stem = Path(args.audio).stem
        out_dir = Path("output") / stem
        out_dir.mkdir(parents=True, exist_ok=True)

        save_task = progress.add_task("Saving output...", total=len(FORMATS))
        for fmt in FORMATS:
            writer = get_writer(fmt, str(out_dir))
            writer(result, args.audio, {})
            progress.advance(save_task)

    print(f"Saved transcription to {out_dir}/")


if __name__ == "__main__":
    main()
