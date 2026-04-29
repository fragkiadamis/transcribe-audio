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
| `--model` | No | Whisper model to use. One of `tiny`, `base`, `small`, `medium`, `large`. Defaults to `base`. |

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
- For better accuracy on difficult audio, use `--model small`, `--model medium`, or `--model large`. Larger models are slower but more accurate.
- GPU acceleration is used automatically if a CUDA-compatible GPU is available.

---

## For developers

### Commits

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. Common types:

| Type | When to use |
|---|---|
| `build` | Build system or external dependency changes |
| `chore` | Tooling, config, dependencies |
| `ci` | CI/CD configuration changes |
| `docs` | Documentation only |
| `feat` | New feature |
| `fix` | Bug fix |
| `perf` | Performance improvement |
| `refactor` | Code change that isn't a fix or feature |
| `revert` | Reverts a previous commit |
| `style` | Formatting, whitespace (no logic change) |
| `test` | Adding or updating tests |
| `bump` | Version bump (automated — do not use manually) |

### Local commit validation

A `commit-msg` hook is included to validate your commit message against the Conventional Commits spec before the commit is created. To install it:

```bash
cp .git/hooks/commit-msg .git/hooks/commit-msg
```

The hook runs automatically — non-conventional messages will be rejected with an explanation.

### Changelog & versioning

Everything is automated. When a PR is merged into `main`, a GitHub Action runs [commitizen](https://commitizen-tools.github.io/commitizen/) to:

- Determine the next version based on commit types since the last release
- Update `pyproject.toml` and `CHANGELOG.md`
- Create a git tag and push the bump commit back to `main`

| Commit type | Version bump |
|---|---|
| `fix` | patch (0.0.**x**) |
| `feat` | minor (0.**x**.0) |
| Breaking change (`!`) | major (**x**.0.0) |

No manual steps needed.
