# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`transcribe-audio` is a Python tool for transcribing audio files using OpenAI Whisper. Sample audio files in `audio/` cover multiple languages (French, English, Greek, Tunisian Arabic). Whisper can produce transcriptions in `.json`, `.srt`, `.tsv`, `.txt`, and `.vtt` formats.

## Package Manager

This project uses `uv`. Always use `uv` commands rather than `pip` or bare `python`.

```bash
uv run python main.py   # run the app
uv add <package>        # add a dependency
uv sync                 # install/sync all dependencies
```

## Key Dependencies

- `openai-whisper` — transcription engine
- `torch` / `torchaudio` / `torchvision` — ML backend required by Whisper
- Requires Python ≥ 3.13
