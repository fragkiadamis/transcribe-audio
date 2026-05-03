# transcribe-audio

Transcribe any audio file locally using [OpenAI Whisper](https://github.com/openai/whisper). No API key needed — everything runs on your machine.

Output is saved to `output/<filename>/` in five formats: `txt`, `srt`, `vtt`, `tsv`, and `json`.
Translation to any language is supported via multiple backends (Google, DeepL, Microsoft, and more).

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

That's it. `uv sync` installs all dependencies (including PyTorch, Whisper, and PySide6) into an isolated virtual environment.

---

## Usage

```bash
uv run main.py
```

This opens the GUI. From there:

1. **Browse** — select an audio file (mp3, wav, ogg, flac, m4a, aac)
2. **Settings** — optionally set language, model, device, and a transcription prompt
3. **Translation** — optionally set a target language, backend, and API key
4. **Transcribe** — click the button and watch progress in real time

Output is written to `output/<filename>/`:

```
output/
└── french/
    ├── transcription.txt   ← plain text
    ├── transcription.srt   ← subtitles (SubRip)
    ├── transcription.vtt   ← subtitles (WebVTT)
    ├── transcription.tsv   ← tab-separated with timestamps
    └── transcription.json  ← full data including segments and metadata
```

---

## Settings reference

| Field | Description |
|---|---|
| Language | 2-letter language code (e.g. `en`, `fr`, `el`). Leave empty for auto-detection. |
| Model | Whisper model: `tiny`, `base`, `small`, `medium`, `large`. Default: `base`. Larger models are slower but more accurate. |
| Device | `auto`, `cpu`, or `cuda`. Default: `auto`. Falls back to CPU automatically on CUDA out-of-memory. |
| Prompt | Optional — guides transcription style or vocabulary (e.g. domain-specific terms). |
| Translate to | Target language code (e.g. `en`, `fr`, `el`). Leave empty to skip translation. |
| Backend | Translation backend. Default: `google`. See [Translators](#translators) below. |
| API Key | Required for some backends. For `papago` and `baidu` use `id:secret` format. |

---

## Supported transcription languages

Any language supported by Whisper. Common codes: `en`, `fr`, `de`, `es`, `it`, `pt`, `el`, `ar`, `zh`, `ja`, `ru`. Full list [here](https://github.com/openai/whisper/blob/main/whisper/tokenizer.py).

---

## Translators

Translation is powered by [deep-translator](https://github.com/nidhaloff/deep-translator). The selected backend translates each segment individually, so timestamps in `.srt` and `.vtt` files remain aligned with the audio.

| Translator | Key | Requires API key |
|---|---|---|
| Google Translate | `google` | No |
| MyMemory | `mymemory` | No |
| Linguee | `linguee` | No |
| Pons | `pons` | No |
| LibreTranslate | `libre` | No (uses public instance) |
| DeepL | `deepl` | Yes — API key |
| Microsoft Translator | `microsoft` | Yes — API key |
| Yandex Translate | `yandex` | Yes — API key |
| QCRI | `qcri` | Yes — API key |
| ChatGPT | `chatgpt` | Yes — API key |
| Papago | `papago` | Yes — `client_id:secret_key` |
| Baidu Translate | `baidu` | Yes — `appid:appkey` |

Supported languages depend on the backend. The default `google` backend supports 133 languages — see the [Google Translate supported languages](https://cloud.google.com/translate/docs/languages). For other backends, refer to their respective documentation.

---

## Notes

- The first run downloads the selected Whisper model and caches it. The `base` model is ~150 MB; `large` is ~3 GB.
- GPU acceleration is used automatically if a CUDA-compatible GPU is available. Select `cpu` if you run into CUDA out-of-memory errors. The `large` model requires ~10 GB of VRAM.
- If CUDA runs out of memory, the tool automatically falls back to CPU without crashing.
- Translation is skipped automatically if the target language matches the detected source language.

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
