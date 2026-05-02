## v1.5.0 (2026-05-02)

### Feat

- add device selection support for Whisper with `--device` flag

## v1.4.0 (2026-05-02)

### Feat

- integrate Rich progress bar with Whisper and tqdm for enhanced task tracking

## v1.3.2 (2026-05-02)

### Refactor

- simplify translation logic and improve translator initialization

## v1.3.1 (2026-05-02)

### Fix

- update release workflow to skip CI for version bumps

## v1.3.0 (2026-05-02)

### Feat

- add support for multiple translation backends and API key configuration
- add translation support with `--translate-to` flag using Google Translator

## v1.2.0 (2026-05-02)

### Feat

- add `--prompt` flag to CLI for setting initial transcription prompt

## v1.1.0 (2026-04-29)

### Feat

- add support for specifying Whisper model via CLI argument

## v1.0.1 (2026-04-29)

### Fix

- Remove post-commit hook

## v1.0.0 (2026-04-29)

### Feat

- Add rich library for progress tracking and enhance transcription feedback
- Save transcriptions to format-specific directories under output
- Add audio transcription functionality with Whisper

### Refactor

- Replace `os` with `pathlib` for improved path handling
