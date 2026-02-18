# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-02-18

**Bug fixes:**
- Fixed `--clean-filler` not filtering filler words from the word list: `--max-chars-per-line` / `--max-words-per-line` subtitle formatters now correctly omit filler words (previously only `seg["text"]` was cleaned; `seg["words"]` was untouched)
- Fixed orphaned punctuation after filler removal: double commas (`,,`), orphaned commas before terminal punctuation (`,?` → `?`), and leading punctuation are now cleaned up correctly
- Fixed fuzzy search comparing short queries against full segment text (always low ratio): now checks individual word tokens so `--search "wrld" --search-fuzzy` correctly matches "world"
- Fixed URL input + `--detect-language-only` not cleaning up downloaded temp directories before exiting; also changed error handling to continue processing remaining files instead of exiting on first error
- Fixed `setup.sh --check` hanging for 60+ seconds when pyannote.audio is installed: now uses `importlib.util.find_spec` + metadata version lookup instead of a full `import pyannote.audio` (avoids slow CUDA/model initialization); check now completes in ~12s
- Fixed `skill.json`: moved `ffmpeg` from `requires.bins` to `optionalBins` — ffmpeg is not required for basic transcription (PyAV handles decoding); only needed for `--burn-in`, `--normalize`, `--denoise`, `--channel`, `--export-speakers`

**Subtitle formats:**
- Added `--format ass` — Advanced SubStation Alpha (Aegisub, VLC, mpv, MPC-HC)
- Added `--format lrc` — Timed lyrics format for music players
- Added `--format html` — Confidence-colored HTML transcript (green/yellow/red per word)
- Added `--format ttml` — W3C TTML 1.0 / DFXP broadcast standard (Netflix, Amazon Prime, BBC)
- Added `--format csv` — Spreadsheet-ready CSV with header row; RFC 4180 quoting; speaker column when diarized

**Transcript tools:**
- Added `--search TERM` — Find timestamps where a word/phrase appears; replaces normal output
- Added `--search-fuzzy` — Approximate matching with `--search`
- Added `--detect-chapters` — Auto-detect chapter breaks from silence gaps
- Added `--chapter-gap SEC`, `--chapters-file PATH`, `--chapter-format youtube|text|json`
- Added `--export-speakers DIR` — Save each diarized speaker's turns as separate WAV files

**Batch improvements:**
- Batch ETA: `[N/total] filename | ETA: Xm Ys` shown automatically for sequential batch jobs
- Added `--language-map "pat=lang,..."` — Per-file language override with fnmatch glob support
- Added `--retries N` — Retry failed files with exponential backoff; failed-file summary at end
- Added `--rss URL` / `--rss-latest N` — Transcribe podcast RSS feeds
- Added `--skip-existing`, `--parallel N`, `--output-template`, `--stats-file`, `--merge-sentences`

**Model & inference:**
- Changed default model to `distil-large-v3.5` (better accuracy than v3)
- Auto-disables `condition_on_previous_text` for distil models (prevents repetition loops)
- Added `--condition-on-previous-text` override; `--log-level` for library debug output
- Added `--model-dir PATH` — Custom HuggingFace cache dir; local CTranslate2 model support
- Added `--no-timestamps`, `--chunk-length`, `--length-penalty`, `--repetition-penalty`, `--no-repeat-ngram-size`
- Added `--clip-timestamps`, `--stream`, `--progress`, `--best-of`, `--patience`, `--max-new-tokens`
- Added `--hotwords`, `--prefix`, `--revision`, `--suppress-tokens`, `--max-initial-timestamp`
- Added `--vad-threshold`, `--vad-neg-threshold`, `--min/max-speech-duration`, `--min-silence-duration`, `--speech-pad`
- Added `--temperature`, `--no-speech-threshold`, `--hallucination-silence-threshold`

**Speaker & quality:**
- Added `--speaker-names "Alice,Bob"` — Replace SPEAKER_1/2 with real names
- Added `--filter-hallucinations` — Remove music/applause markers, duplicates, artifacts
- Added `--burn-in OUTPUT` — Burn subtitles into video via ffmpeg
- Added `--keep-temp` — Preserve URL-downloaded audio for re-processing
- Added `--min-speakers` / `--max-speakers` hints for diarization

**Setup & agent compatibility:**
- Added `setup.sh --check` — System diagnostic
- ffmpeg no longer required for basic transcription (PyAV handles decoding)
- Expanded trigger phrases and agent guidance for all new features
- Chapter stdout output now uses `=== CHAPTERS (N) ===` separator for clean agent parsing
- Fixed: `--quiet` / `-q` now correctly suppresses the RTX 3070 compute-type tip
- Fixed: `--format json --detect-chapters` now embeds chapters under `"chapters"` key in JSON output

## [1.0.1] - 2026-01-28

Remove install metadata; add python3 to required binaries

## [1.0.0] - 2026-01-28

Initial release: Local speech-to-text using faster-whisper with 4-6x speed boost over OpenAI Whisper. GPU acceleration enables ~20x realtime transcription. Auto-setup scripts for Windows/Linux/macOS with CUDA detection. Supports distilled models for 6x additional speedup.
