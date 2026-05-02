import argparse
from pathlib import Path

import whisper
from deep_translator import (
    BaiduTranslator,
    ChatGptTranslator,
    DeeplTranslator,
    GoogleTranslator,
    LibreTranslator,
    LingueeTranslator,
    MicrosoftTranslator,
    MyMemoryTranslator,
    PapagoTranslator,
    PonsTranslator,
    QcriTranslator,
    YandexTranslator,
)
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from whisper.utils import get_writer

FORMATS = ("json", "srt", "tsv", "vtt", "txt")

TRANSLATORS = {
    "google": GoogleTranslator,
    "mymemory": MyMemoryTranslator,
    "linguee": LingueeTranslator,
    "pons": PonsTranslator,
    "libre": LibreTranslator,
    "deepl": DeeplTranslator,
    "microsoft": MicrosoftTranslator,
    "yandex": YandexTranslator,
    "qcri": QcriTranslator,
    "chatgpt": ChatGptTranslator,
    "papago": PapagoTranslator,
    "baidu": BaiduTranslator,
}

_SINGLE_KEY = {"deepl", "microsoft", "yandex", "qcri", "chatgpt", "libre"}
_DUAL_KEY = {"papago", "baidu"}
_REQUIRES_KEY = _SINGLE_KEY | _DUAL_KEY


def _build_translator(name, source, target, api_key):
    cls = TRANSLATORS[name]
    if name in _SINGLE_KEY:
        return cls(source=source, target=target, api_key=api_key)
    if name == "papago":
        client_id, secret_key = api_key.split(":", 1)
        return cls(source=source, target=target, client_id=client_id, secret_key=secret_key)
    if name == "baidu":
        appid, appkey = api_key.split(":", 1)
        return cls(source=source, target=target, appid=appid, appkey=appkey)
    return cls(source=source, target=target)


def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Whisper")
    parser.add_argument("audio", help="Path to the audio file")
    parser.add_argument("-l", "--lang", help="2-letter language code (e.g. en, fr, ar, el)")
    parser.add_argument("-m", "--model", default="base", choices=["tiny", "base", "small", "medium", "large"], help="Whisper model to use (default: base)")
    parser.add_argument("-p", "--prompt", help="Initial prompt to guide transcription style or vocabulary")
    parser.add_argument("-t", "--translate-to", dest="translate_to", metavar="LANG", help="Translate output to this language (e.g. en, fr, el). Use 'en' for Whisper's built-in translation, or any Google Translate language code for others.")
    parser.add_argument("--translator", default="google", choices=TRANSLATORS, help="Translation backend to use (default: google)")
    parser.add_argument("--api-key", dest="api_key", metavar="KEY", help="API key for the selected translator. For papago and baidu use 'id:secret' format.")
    args = parser.parse_args()

    if args.lang is not None and len(args.lang) != 2:
        parser.error("Language code must be exactly 2 letters")

    if args.translate_to and args.translate_to != "en":
        if args.translator in _REQUIRES_KEY and not args.api_key:
            parser.error(f"--translator {args.translator} requires --api-key")
        if args.translator in _DUAL_KEY and args.api_key and ":" not in args.api_key:
            parser.error(f"--translator {args.translator} requires --api-key in 'id:secret' format")

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
        if args.translate_to == "en":
            transcribe_kwargs["task"] = "translate"

        transcribe_task = progress.add_task("Transcribing...", total=None)
        result = model.transcribe(args.audio, verbose=None, **transcribe_kwargs)
        progress.update(transcribe_task, completed=True, total=1, description="Transcription done")

        if args.translate_to and args.translate_to != args.lang:
            translate_task = progress.add_task("Translating...", total=None)
            translator = _build_translator(args.translator, "auto", args.translate_to, args.api_key)
            result["text"] = translator.translate(result["text"])
            for segment in result["segments"]:
                segment["text"] = translator.translate(segment["text"])
            progress.update(translate_task, completed=True, total=1, description="Translation done")

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
