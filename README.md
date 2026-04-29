# transcribe-audio

Transcribe any audio file locally using [OpenAI Whisper](https://github.com/openai/whisper). No API key needed — everything runs on your machine.

Output is saved to `output/<filename>/` in five formats: `txt`, `srt`, `vtt`, `tsv`, and `json`.

---

## Requirements

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
- FFmpeg (see below)

---

## Install FFmpeg

Whisper requires FFmpeg to be available on your system before running.

**macOS**
```bash
brew install ffmpeg
```

**Ubuntu / Debian**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows**

First, install [Chocolatey](https://chocolatey.org/) if you don't have it. Open PowerShell as Administrator and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

Verify with `choco --version`, then install FFmpeg:

```powershell
choco install ffmpeg
```

Verify it works with `ffmpeg -version`.

---

## Installation

```bash
pip install uv
git clone https://github.com/fragkiadamis/transcribe-audio.git
cd transcribe-audio
uv sync
```

That's it. `uv sync` installs all dependencies (including PyTorch and Whisper) into an isolated virtual environment.

---

## Usage

```bash
uv run main.py <audio-file> [lang]
```

| Argument | Required | Description |
|---|---|---|
| `audio-file` | Yes | Path to the audio file (mp3, wav, ogg, …) |
| `lang` | No | 2-letter language code. If omitted, Whisper auto-detects the language. |

### Examples

```bash
# Auto-detect language
uv run main.py audio/interview.mp3

# French audio
uv run main.py audio/french.mp3 fr

# Greek audio
uv run main.py audio/greek.mp3 el
```

Output is written to `output/<filename>/`:

```
output/
└── french/
    ├── french.txt   ← plain text
    ├── french.srt   ← subtitles (SubRip)
    ├── french.vtt   ← subtitles (WebVTT)
    ├── french.tsv   ← tab-separated with timestamps
    └── french.json  ← full data including segments and metadata
```

---

## Supported languages

Any language supported by Whisper. Common codes: `en`, `fr`, `de`, `es`, `it`, `pt`, `el`, `ar`, `zh`, `ja`, `ru`. Full list [here](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py).

---

## Notes

- The first run downloads the `base` Whisper model (~150 MB) and caches it automatically.
- For better accuracy on difficult audio, the model size can be changed to `small`, `medium`, or `large` in `main.py`.
- GPU acceleration is used automatically if a CUDA-compatible GPU is available.

---

## For developers

### Commits

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. Common types:

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change that isn't a fix or feature |
| `docs` | Documentation only |
| `chore` | Tooling, config, dependencies |

### Changelog

`CHANGELOG.md` is generated automatically after every commit via a post-commit hook powered by [commitizen](https://commitizen-tools.github.io/commitizen/). No manual steps needed.

### Versioning

The project uses [semantic versioning](https://semver.org/). When ready to release, run:

```bash
uv run cz bump
```

This inspects the commits since the last tag, determines the next `major.minor.patch` version, updates it in `pyproject.toml`, regenerates `CHANGELOG.md`, and creates a git tag.

| Commit type | Version bump |
|---|---|
| `fix` | patch (0.0.**x**) |
| `feat` | minor (0.**x**.0) |
| Breaking change (`!`) | major (**x**.0.0) |
