# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-02-18

### Bug fixes

- Fixed `--clean-filler` not stripping filler words from the word list — subtitle formatters (`--max-chars-per-line` / `--max-words-per-line`) use the word list directly, so filler words reappeared in SRT/VTT/ASS/TTML output
- Fixed orphaned punctuation after filler removal (double commas, leading commas, `,?` → `?`)
- Fixed `--search-fuzzy` always failing on short queries — now matches per word token (similarity ≥0.6) instead of comparing the short query against full segment text
- Fixed URL + `--detect-language-only` leaving temp directories behind; also changed errors to continue remaining files instead of aborting the batch
- Fixed `setup.sh --check` hanging 60+ seconds when pyannote.audio is installed — now uses lightweight metadata lookup instead of a full import; completes in ~12s
- Fixed `skill.json`: moved `ffmpeg` from `requires.bins` to `optionalBins` — only needed for `--burn-in`, `--normalize`, `--denoise`, `--channel`, `--export-speakers`

### Subtitle formats

- **`--format ass`** — Advanced SubStation Alpha subtitles (Aegisub, mpv, VLC, MPC-HC); supports `--max-words-per-line` and diarization labels
- **`--format lrc`** — Timed lyrics format for music players (foobar2000, AIMP, VLC)
- **`--format html`** — Confidence-colored HTML transcript: green (≥0.8), yellow (≥0.5), red (<0.5); requires `--word-timestamps`
- **`--format ttml`** — W3C TTML 1.0 / DFXP broadcast subtitles (Netflix, Amazon Prime, BBC)
- **`--format csv`** — RFC 4180 CSV with header row; speaker column auto-added when `--diarize` is set

### Transcript tools

- **`--search TERM`** — Find all timestamps where a word/phrase appears; replaces normal transcript output
- **`--search-fuzzy`** — Approximate matching with `--search` (similarity ≥0.6 per token); finds "wrld" → "world"
- **`--detect-chapters`** — Auto-detect chapter breaks from silence gaps; outputs YouTube-style timestamps
- **`--chapter-gap SEC`** — Minimum silence for a chapter break (default: 8s); lower for dense content
- **`--chapters-file PATH`** — Save chapters to a file so they don't mix into the transcript; avoid in batch mode (single path gets overwritten per file)
- **`--chapter-format youtube|text|json`** — Format for chapter output; `youtube` (default) is paste-ready for YouTube descriptions; with `--format json`, chapters embed under a `"chapters"` key
- **`--export-speakers DIR`** — Post-diarization, save each speaker's audio turns as separate WAV files; requires `--diarize` and ffmpeg

### Batch improvements

- **Batch ETA** (no flag) — Automatically shows `[N/total] filename | ETA: Xm Ys` for sequential batch jobs
- **`--language-map "pat=lang,..."`** — Per-file language override in batch using fnmatch globs; also accepts `@file.json`
- **`--retries N`** — Retry failed files with exponential backoff (2s, 4s, 8s…); shows failed-file summary at end; ignored in `--parallel` mode
- **`--rss URL`** — Download and transcribe podcast episodes from an RSS feed; always pair with `-o <dir>`
- **`--rss-latest N`** — Number of episodes to fetch from RSS (default: 5; 0 = all)
- **`--skip-existing`** — Skip files that already have output; safe for resuming interrupted batches
- **`--parallel N`** — Process N files simultaneously; mainly useful for CPU batch jobs (GPU handles one file efficiently on its own)
- **`--output-template`** — Custom filename pattern for batch output (e.g., `"{stem}_{lang}.{ext}"`)
- **`--stats-file PATH`** — Write performance stats JSON (duration, processing time, RTF) after transcription; pass a dir in batch mode for one file per input
- **`--merge-sentences`** — Merge short fragment segments into sentence-length chunks before writing

### Model & inference

- **Default model → `distil-large-v3.5`** — Better accuracy (7.08 vs 7.53 WER), same speed; trained on 4× more data
- **Auto-disable `condition_on_previous_text` for distil-* models** — Prevents repetition loops; HuggingFace recommendation; applied automatically, no flag needed
- **`--condition-on-previous-text`** — Override to re-enable context conditioning (off by default for distil models)
- **`--log-level debug|info|warning|error`** — Control faster-whisper library verbosity; `debug` for diagnosing issues, `error` for clean pipeline output
- **`--model-dir PATH`** — Custom HuggingFace model cache dir; also works with locally converted CTranslate2 models
- **`--no-timestamps`** — Output plain text only, no timestamps
- **`--chunk-length SEC`** — Audio chunk size for batched inference; smaller = less memory, may affect accuracy at boundaries
- **`--length-penalty FLOAT`** — Bias beam search toward shorter (<1.0) or longer (>1.0) outputs
- **`--repetition-penalty FLOAT`** — Penalize repeated phrases; values >1.0 reduce looping
- **`--no-repeat-ngram-size N`** — Hard-block any N-gram from appearing twice in output
- **`--clip-timestamps "START,END"`** — Transcribe only between START and END seconds (e.g., `"30,60"`)
- **`--stream`** — Print segments progressively as transcribed instead of waiting for the full file
- **`--progress`** — Show a progress bar during transcription
- **`--best-of N`** — Sample N candidates in greedy mode and pick the best; higher = more accurate but slower
- **`--patience FLOAT`** — Beam search patience multiplier; >1.0 explores more hypotheses at cost of speed
- **`--max-new-tokens N`** — Max tokens generated per audio chunk; limits runaway generation on silence/music
- **`--hotwords WORDS`** — Boost specific words in the decoder; unlike `--initial-prompt`, directly biases token probabilities; best for rare terms that keep getting missed
- **`--prefix TEXT`** — Seed the first segment with known opening text; only affects the first chunk
- **`--revision VERSION`** — Pin a specific HuggingFace model revision for reproducible transcription
- **`--suppress-tokens`** — Comma-separated token IDs to block during decoding
- **`--max-initial-timestamp FLOAT`** — Cap the timestamp of the first token; prevents long leading silences from being misread
- **`--vad-threshold FLOAT`** (default: 0.5) — Speech detection sensitivity; raise to 0.6–0.7 if background noise is being transcribed
- **`--vad-neg-threshold FLOAT`** — Hysteresis threshold; speech ends only when probability drops below this
- **`--min-speech-duration-ms MS`** — Minimum segment length to count as speech; raise to filter short noise bursts
- **`--max-speech-duration-s SEC`** — Maximum segment length; longer segments are split at this boundary
- **`--min-silence-duration-ms MS`** — Minimum gap between segments; increase to join segments split by brief pauses
- **`--speech-pad-ms MS`** — Padding around detected speech; increase to avoid clipping word edges
- **`--temperature FLOAT`** — Decoding temperature; 0.0 = greedy/deterministic (recommended); higher adds randomness
- **`--no-speech-threshold FLOAT`** — Drop segments where no-speech probability exceeds this; raise to 0.8 to reject music/silence hallucinations
- **`--hallucination-silence-threshold FLOAT`** — Drop segments where Whisper generates text over near-silence; helps with ambient music or background noise

### Speaker & quality

- **`--speaker-names "Alice,Bob"`** — Replace `SPEAKER_1`/`SPEAKER_2` with real names in order; requires `--diarize`; also renames WAV files from `--export-speakers`
- **`--filter-hallucinations`** — Remove sound markers (`[Music]`, `[Applause]`), common outros, and exact-duplicate consecutive segments
- **`--burn-in OUTPUT`** — Burn subtitles into a video as a hard-coded overlay via ffmpeg; requires a video input and ffmpeg
- **`--keep-temp`** — Keep URL-downloaded audio after transcription; avoids re-downloading if you re-process the same URL
- **`--min-speakers N` / `--max-speakers N`** — Hint pyannote about expected speaker count; improves diarization when you already know it (e.g., `--min-speakers 2 --max-speakers 2` for a 1-on-1)

### Audio preprocessing

- **`--clean-filler`** — Strip `um`, `uh`, `er`, `ah`, `hmm`, `you know`, `I mean`, `you see` from output; filters both segment text and word list so subtitles also omit them
- **`--channel left|right|mix`** — Extract one stereo channel before transcribing (default: `mix`); useful for dual-speaker interviews where each person is on one channel
- **`--max-chars-per-line N`** — Character-based subtitle wrapping (e.g., 42 for Netflix style); takes priority over `--max-words-per-line`
- **`--detect-paragraphs`** — Insert `\n\n` breaks in text output at natural pause/sentence boundaries
- **`--paragraph-gap SEC`** — Gap threshold for paragraph detection (default: 3.0s); lower for fast-paced speech

### Setup & agent compatibility

- **`setup.sh --check`** — System diagnostic: GPU/CUDA, Python, ffmpeg, venv, faster-whisper, pyannote.audio, yt-dlp, HuggingFace token
- **ffmpeg now optional** — PyAV handles basic decoding; ffmpeg only needed for `--burn-in`, `--normalize`, `--denoise`, `--channel`, `--export-speakers`
- **Chapter stdout uses `=== CHAPTERS (N) ===` separator** — Makes it easy for scripts/agents to split chapter data from transcript text
- **`--quiet` / `-q` now suppresses the RTX 3070 compute-type tip**
- **`--format json --detect-chapters`** — Chapters now embedded under `"chapters"` key in JSON output

---

## [1.0.1] - 2026-01-28

Remove install metadata; add python3 to required binaries

## [1.0.0] - 2026-01-28

Initial release: Local speech-to-text using faster-whisper with 4-6x speed boost over OpenAI Whisper. GPU acceleration enables ~20x realtime transcription. Auto-setup scripts for Windows/Linux/macOS with CUDA detection. Supports distilled models for 6x additional speedup.
