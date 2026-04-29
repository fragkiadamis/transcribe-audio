import argparse
from pathlib import Path

import whisper
from whisper.utils import get_writer


def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Whisper")
    parser.add_argument("audio", help="Path to the audio file")
    parser.add_argument("lang", nargs="?", help="2-letter language code (e.g. en, fr, ar, el)")
    args = parser.parse_args()

    if args.lang is not None and len(args.lang) != 2:
        parser.error("Language code must be exactly 2 letters")

    model = whisper.load_model("base")

    transcribe_kwargs = {}
    if args.lang:
        transcribe_kwargs["language"] = args.lang

    result = model.transcribe(args.audio, verbose=False, **transcribe_kwargs)

    stem = Path(args.audio).stem
    out_dir = Path("output") / stem
    out_dir.mkdir(parents=True, exist_ok=True)

    for fmt in ("json", "srt", "tsv", "vtt", "txt"):
        writer = get_writer(fmt, str(out_dir))
        writer(result, args.audio, {})

    print(f"Saved transcription to {out_dir}/")


if __name__ == "__main__":
    main()
