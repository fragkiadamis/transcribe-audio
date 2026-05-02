import argparse
import tqdm as tqdm_module
import warnings
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


def _rich_tqdm_class(progress, task_id):
    """Returns a tqdm-compatible class that routes progress updates to a Rich task."""
    class _T:
        def __init__(self, *args, total=None, **kwargs):
            if total is not None:
                progress.update(task_id, total=total)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def update(self, n=1):
            progress.advance(task_id, n)

        def close(self):
            pass

        def set_postfix(self, **kwargs):
            pass

    return _T


def _complete_task(progress, task_id, description):
    """Marks a Rich task as 100% complete, handling both determinate and indeterminate tasks."""
    task = next(t for t in progress.tasks if t.id == task_id)
    total = task.total if task.total is not None else 1
    progress.update(task_id, completed=total, total=total, description=description)


def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file using Whisper")
    parser.add_argument("audio", help="Path to the audio file")
    parser.add_argument("-l", "--lang", help="2-letter language code (e.g. en, fr, ar, el)")
    parser.add_argument("-m", "--model", default="base", choices=["tiny", "base", "small", "medium", "large"], help="Whisper model to use (default: base)")
    parser.add_argument("-p", "--prompt", help="Initial prompt to guide transcription style or vocabulary")
    parser.add_argument("-t", "--translate-to", dest="translate_to", metavar="LANG", help="Translate output to this language (e.g. en, fr, el)")
    parser.add_argument("--translator", default="google", choices=TRANSLATORS, help="Translation backend to use (default: google)")
    parser.add_argument("--api-key", dest="api_key", metavar="KEY", help="API key for the selected translator. For papago and baidu use 'id:secret' format.")
    parser.add_argument("-d", "--device", default="auto", choices=["auto", "cpu", "cuda"], help="Device to run Whisper on: auto, cpu, or cuda (default: auto)")
    args = parser.parse_args()

    if args.lang is not None and len(args.lang) != 2:
        parser.error("Language code must be exactly 2 letters")

    if args.translate_to:
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
        # Model loading — patch whisper.tqdm (from tqdm import tqdm in whisper/__init__.py)
        load_task = progress.add_task("Loading model...", total=None)
        device = args.device if args.device != "auto" else ("cuda" if whisper.torch.cuda.is_available() else "cpu")
        _orig_whisper_tqdm = whisper.tqdm
        whisper.tqdm = _rich_tqdm_class(progress, load_task)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                model = whisper.load_model(args.model, device=device)
            except RuntimeError:
                device = "cpu"
                model = whisper.load_model(args.model, device=device)
        whisper.tqdm = _orig_whisper_tqdm
        _complete_task(progress, load_task, "Model loaded")

        # Transcription — patch tqdm.tqdm (import tqdm; tqdm.tqdm(...) in transcribe.py)
        transcribe_kwargs = {}
        if args.lang:
            transcribe_kwargs["language"] = args.lang
        if args.prompt:
            transcribe_kwargs["initial_prompt"] = args.prompt
        if device == "cpu":
            transcribe_kwargs["fp16"] = False
        transcribe_task = progress.add_task("Transcribing...", total=None)
        _orig_tqdm = tqdm_module.tqdm
        tqdm_module.tqdm = _rich_tqdm_class(progress, transcribe_task)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = model.transcribe(args.audio, verbose=False, **transcribe_kwargs)
        tqdm_module.tqdm = _orig_tqdm
        _complete_task(progress, transcribe_task, "Transcription done")

        source_lang = result.get("language") or args.lang
        if args.translate_to and args.translate_to != source_lang:
            segments = result["segments"]
            translate_task = progress.add_task("Translating...", total=len(segments))
            translator = _build_translator(args.translator, source_lang or "auto", args.translate_to, args.api_key)
            translated_segments = []
            for segment in segments:
                segment["text"] = translator.translate(segment["text"])
                translated_segments.append(segment["text"])
                progress.advance(translate_task)
            result["text"] = " ".join(translated_segments)
            progress.update(translate_task, description="Translation done")

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
