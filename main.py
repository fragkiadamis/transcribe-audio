import argparse

from core.transcriber import Transcriber
from core.translator import TRANSLATORS, Translator
from core.writer import FORMATS, OutputWriter
from ui.progress import ProgressManager


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

    transcriber = Transcriber(model_name=args.model, device=args.device)
    try:
        translator = Translator(backend=args.translator, target=args.translate_to, api_key=args.api_key)
    except ValueError as e:
        parser.error(str(e))
    writer = OutputWriter(audio_path=args.audio)

    with ProgressManager() as pm:
        with pm.loading():
            transcriber.load()

        with pm.transcribing():
            result = transcriber.transcribe(args.audio, lang=args.lang, prompt=args.prompt)

        source_lang = result.get("language") or args.lang
        if args.translate_to and args.translate_to != source_lang:
            with pm.translating(total=len(result["segments"])) as cb:
                result = translator.translate(result, on_progress=cb)

        with pm.saving(total=len(FORMATS)) as cb:
            out_dir = writer.write(result, on_progress=cb)

    print(f"Saved transcription to {out_dir}/")


if __name__ == "__main__":
    main()
