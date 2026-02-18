# faster-whisper

A skill for your OpenClaw agent that uses faster-whisper to transcribe audio more quickly.

faster-whisper is superior to OpenAI's Whisper — it's a CTranslate2 reimplementation that's ~4-6x faster with identical accuracy.

## Note on Antivirus/VirusTotal Flags

Some scanners (including VirusTotal on ClawHub) may flag this skill as "suspicious" as a specially crafted URL or file path could potentially exploit a command injection flaw within `yt-dlp` or `ffmpeg`.

I swear that I am not distributing any malware — this is a normal risk of any tool that downloads and processes files from the internet. As with any such tool: be mindful of what you feed it and always back up your important files.

## Features

### Key Features

- **~4-6x faster** than OpenAI's original Whisper (same model weights, CTranslate2 backend)
- **~20x realtime** with GPU — transcribe 10 min of audio in ~30 sec
- **Distilled models** available (~6x faster again with <1% WER loss)
- **Speaker diarization** (`--diarize`) — labels who said what via pyannote.audio
- **GPU acceleration** (NVIDIA CUDA) with quantization for CPU efficiency

### Other Features

- **YouTube/URL input** — auto-downloads via yt-dlp (YouTube, direct links, etc.)
- **Subtitle output** — SRT, VTT, ASS, LRC, TTML, HTML formats
- **Word-level timestamps** with automatic wav2vec2 alignment (~10ms precision)
- **Voice activity detection (VAD)** — removes silence automatically (on by default)
- **Audio preprocessing** — normalize volume (`--normalize`) and denoise (`--denoise`)
- **Filler word removal** (`--clean-filler`) — strip um/uh/er/ah/hmm and discourse markers
- **Transcript search** (`--search TERM`) — find all timestamps where a word/phrase appears
- **Chapter detection** (`--detect-chapters`) — auto-detect sections from silence gaps
- **CSV/TSV output** — spreadsheet-ready transcripts with proper quoting
- **Paragraph detection** (`--detect-paragraphs`) — insert natural paragraph breaks in text output
- **Podcast RSS transcription** (`--rss URL`) — fetch and transcribe episodes from a feed
- **Stereo channel selection** (`--channel left|right`) — transcribe a specific stereo track
- **Speaker audio export** (`--export-speakers DIR`) — save each speaker's turns as separate WAV files
- **Batch processing** with automatic ETA — glob patterns, directories, skip-existing
- **Translation to English** (`--translate`) — any language → English
- **Multilingual support** (99+ languages with auto-detection)

## Installation

### Option 1: Install from ClawHub

**Via CLI** (no installation required):

```bash
# Using npx (npm)
npx clawdhub@latest install faster-whisper

# Using pnpm
pnpm dlx clawdhub@latest install faster-whisper

# Using bun
bunx clawdhub@latest install faster-whisper
```

This downloads and installs the skill into your default skills directory (`~/clawd/your-agent/workspace/skills/` or similar).

**Via Web UI:**

1. Go to https://clawdhub.com/ThePlasmak/faster-whisper
2. Download the zip
3. Unzip the zip and move the contents into a `faster-whisper` folder in your skills directory.

### Option 2: Download from GitHub Releases

1. Go to [Releases](https://github.com/ThePlasmak/faster-whisper/releases)
2. Download the latest `faster-whisper-X.X.X.zip`
3. Extract it to your agent's skills folder:
   - **Default location**: `~/clawd/your-agent/workspace/skills/faster-whisper`
   - Or wherever your agent's workspace is configured

```bash
# Example
cd ~/clawd/your-agent/workspace/skills/
unzip ~/Downloads/faster-whisper-1.0.1.zip -d faster-whisper
```

**If you're lazy:** You can also ask your agent to install it by pasting this repo's link (https://github.com/ThePlasmak/faster-whisper) directly in the chat.

**Note:** The release zip excludes certain explanatory files (CHANGELOG, LICENSE, README) and only contains the skill itself — this keeps things lightweight.

## Setup

### Using With Your Agent

If you're using your agent, it can guide you through the installation automatically.

**What your agent does:**

- Detects your platform (Windows/Linux/macOS/WSL2)
- Checks for Python and GPU drivers
- Runs the appropriate setup script for you

### Standalone CLI Setup

If you want to use the transcription scripts directly without your agent:

**Linux / macOS / WSL2:**
```bash
# Base install (creates venv, installs deps, auto-detects GPU)
./setup.sh

# With speaker diarization support
./setup.sh --diarize
```

**Windows (Native):**
```powershell
.\setup.ps1   # Auto-installs Python via winget if needed
```

**What it installs:**
- Python 3.10+ (if missing)
- faster-whisper + dependencies (PyAV included for audio decoding)
- CUDA support (if NVIDIA GPU detected)
- Optional: pyannote.audio (via `./setup.sh --diarize`)

**Note:** ffmpeg is **not required** for basic transcription — PyAV (bundled with faster-whisper) handles audio decoding automatically. ffmpeg is only needed if you use `--burn-in`, `--normalize`, `--denoise`, `--channel`, or `--export-speakers`.

## How to Use

### With Your Agent

Just ask in natural language:

```
"Transcribe this audio file" (with file attached)
"Transcribe interview.mp3 with word timestamps"
"Transcribe this in Spanish"
"Transcribe this and save as JSON"
"Who's speaking in this recording?"
"Generate SRT subtitles for this video"
"Translate this audio to English"
```

Your agent will:
- Use the GPU if available
- Handle errors and suggest fixes
- Return formatted results

### Standalone CLI

Run the transcription script directly:

**Linux / macOS / WSL2:**
```bash
./scripts/transcribe audio.mp3
```

**Windows:**
```powershell
.\scripts\transcribe.cmd audio.mp3
```

#### CLI Examples

```bash
# Basic transcription
./scripts/transcribe audio.mp3

# SRT subtitles
./scripts/transcribe audio.mp3 --format srt -o subtitles.srt

# JSON output with full metadata
./scripts/transcribe audio.mp3 --format json -o out.json

# Speaker diarization (who said what)
./scripts/transcribe meeting.wav --diarize

# YouTube / URL input (auto-downloads)
./scripts/transcribe https://youtube.com/watch?v=... --language en

# Batch process with skip-existing (resume interrupted batches)
./scripts/transcribe *.mp3 --skip-existing -o ./transcripts/

# Search for a keyword and get timestamps
./scripts/transcribe audio.mp3 --search "keyword"

# Auto-detect chapter/section breaks
./scripts/transcribe audio.mp3 --detect-chapters

# Transcribe a podcast RSS feed (latest 5 episodes)
./scripts/transcribe --rss https://feeds.example.com/podcast.xml -o ./episodes/

# Translate any language to English
./scripts/transcribe audio.mp3 --translate

# Remove filler words (um, uh, you know, I mean...)
./scripts/transcribe audio.mp3 --clean-filler

# Denoise and normalize noisy audio before transcribing
./scripts/transcribe audio.mp3 --denoise --normalize

# Specify language (faster than auto-detect)
./scripts/transcribe podcast.mp3 --language en

# High-accuracy mode
./scripts/transcribe lecture.wav --model large-v3 --beam-size 10

# Fast English-only transcription
./scripts/transcribe audio.mp3 --model distil-medium.en --language en

# Diarized VTT subtitles with named speakers
./scripts/transcribe meeting.wav --diarize --speaker-names "Alice,Bob" --format vtt -o meeting.vtt

# Transcribe only the left stereo channel
./scripts/transcribe audio.mp3 --channel left

# Write SRT and plain text simultaneously
./scripts/transcribe audio.mp3 --format srt,text -o ./out/

# Multi-format output with custom filenames
./scripts/transcribe audio.mp3 --format srt,text -o ./out/ --output-template "{stem}_{lang}.{ext}"
```

#### CLI Options

Options are grouped by category below. Run `./scripts/transcribe --help` for the full reference.

---

**Input**

| Option | Description |
|--------|-------------|
| `AUDIO` | Audio file(s), directory, glob pattern, or URL. Accepts: mp3, wav, m4a, flac, ogg, webm, mp4, mkv, avi, wma, aac. URLs auto-download via yt-dlp. |

---

**Model & Language**

| Option | Short | Description |
|--------|-------|-------------|
| `--model NAME` | `-m` | Whisper model (default: `distil-large-v3.5`; `"turbo"` = large-v3-turbo) |
| `--revision REV` | | Pin a specific model revision (git branch/tag/commit) |
| `--language CODE` | `-l` | Language code, e.g. `en`, `es`, `fr` (auto-detects if omitted) |
| `--language-map MAP` | | Per-file language override for batch mode: `"interview*.mp3=en,lecture.wav=fr"` or `@map.json` |
| `--initial-prompt TEXT` | | Prompt to condition the model (terminology, formatting hints) |
| `--prefix TEXT` | | Prefix to condition the first segment with known opening words |
| `--hotwords WORDS` | | Space-separated hotwords to boost recognition |
| `--translate` | | Translate any language to English instead of transcribing |
| `--multilingual` | | Enable multilingual/code-switching mode |
| `--hf-token TOKEN` | | HuggingFace token for private/gated models and diarization |
| `--model-dir PATH` | | Custom model cache directory (default: `~/.cache/huggingface/`) |

---

**Output Format**

| Option | Short | Description |
|--------|-------|-------------|
| `--format FMT` | `-f` | `text` \| `json` \| `srt` \| `vtt` \| `tsv` \| `csv` \| `lrc` \| `html` \| `ass` \| `ttml` (default: `text`). Accepts comma-separated list: `--format srt,text` |
| `--output PATH` | `-o` | Output file or directory (directory required for batch and multi-format) |
| `--output-template TMPL` | | Batch filename template. Variables: `{stem}`, `{lang}`, `{ext}`, `{model}` |
| `--word-timestamps` | | Include word-level timestamps (wav2vec2 aligned automatically) |
| `--stream` | | Output segments as they are transcribed (disables diarize/alignment) |
| `--merge-sentences` | | Merge segments into sentence-level chunks (improves SRT/VTT readability) |
| `--max-words-per-line N` | | For SRT/VTT, split long cues into sub-cues of at most N words |
| `--max-chars-per-line N` | | For SRT/VTT/ASS/TTML, split lines to fit within N characters (takes priority over `--max-words-per-line`) |
| `--clean-filler` | | Remove hesitation fillers (um, uh, er, ah, hmm) and discourse markers (you know, I mean) |
| `--detect-paragraphs` | | Insert paragraph breaks in text output at natural boundaries |
| `--paragraph-gap SEC` | | Minimum silence gap to start a new paragraph (default: 3.0s) |
| `--channel {left,right,mix}` | | Stereo channel to transcribe (default: `mix`). Requires ffmpeg. |

---

**Inference Tuning**

| Option | Description |
|--------|-------------|
| `--beam-size N` | Beam search size; higher = more accurate but slower (default: 5) |
| `--temperature T` | Sampling temperature or comma-separated fallback list (e.g. `0.0,0.2,0.4`) |
| `--no-speech-threshold PROB` | Probability threshold to treat segments as silence (default: 0.6) |
| `--batch-size N` | Batched inference batch size (default: 8; reduce if OOM) |
| `--no-vad` | Disable voice activity detection (VAD is on by default) |
| `--vad-threshold T` | VAD speech probability threshold (default: 0.5) |
| `--vad-neg-threshold T` | VAD negative threshold for ending speech |
| `--min-speech-duration MS` | Minimum speech segment duration in ms |
| `--max-speech-duration SEC` | Maximum speech segment duration in seconds |
| `--min-silence-duration MS` | Minimum silence before splitting a segment in ms (default: 2000) |
| `--speech-pad MS` | Padding around speech segments in ms (default: 400) |
| `--hallucination-silence-threshold SEC` | Skip silent sections where model hallucinates (e.g. `1.0`) |
| `--no-condition-on-previous-text` | Don't condition on previous text (auto-enabled for distil models) |
| `--condition-on-previous-text` | Force-enable previous-text conditioning (overrides auto-disable for distil models) |
| `--compression-ratio-threshold RATIO` | Filter segments above this compression ratio (default: 2.4) |
| `--log-prob-threshold PROB` | Filter segments below this avg log probability (default: -1.0) |
| `--no-speech-threshold PROB` | Probability threshold to mark segments as no-speech (default: 0.6) |
| `--max-new-tokens N` | Maximum tokens per segment (prevents runaway generation) |
| `--clip-timestamps RANGE` | Transcribe specific time ranges: `30,60` or `0,30;60,90` (seconds) |
| `--progress` | Show transcription progress bar |
| `--best-of N` | Candidates when sampling with non-zero temperature (default: 5) |
| `--patience F` | Beam search patience factor (default: 1.0) |
| `--repetition-penalty F` | Penalty for repeated tokens (default: 1.0) |
| `--no-repeat-ngram-size N` | Prevent n-gram repetitions of this size (default: 0 = off) |
| `--no-batch` | Disable batched inference (use standard WhisperModel) |

---

**Advanced Inference**

| Option | Description |
|--------|-------------|
| `--no-timestamps` | Output text without timing info (faster; incompatible with word timestamps, SRT/VTT/TSV, diarize) |
| `--chunk-length N` | Audio chunk length in seconds for batched inference (default: auto) |
| `--language-detection-threshold T` | Confidence threshold for language auto-detection (default: 0.5) |
| `--language-detection-segments N` | Audio segments to sample for language detection (default: 1) |
| `--length-penalty F` | Beam search length penalty; >1 favors longer outputs (default: 1.0) |
| `--prompt-reset-on-temperature T` | Reset initial prompt when temperature fallback hits threshold (default: 0.5) |
| `--no-suppress-blank` | Disable blank token suppression (may help soft/quiet speech) |
| `--suppress-tokens IDS` | Comma-separated token IDs to suppress in addition to default |
| `--max-initial-timestamp T` | Maximum timestamp for the first segment in seconds (default: 1.0) |
| `--prepend-punctuations CHARS` | Punctuation merged into the preceding word |
| `--append-punctuations CHARS` | Punctuation merged into the following word |

---

**Preprocessing**

| Option | Description |
|--------|-------------|
| `--normalize` | Normalize audio volume (EBU R128 loudnorm) before transcription. Requires ffmpeg. |
| `--denoise` | Apply noise reduction (high-pass + FFT denoise) before transcription. Requires ffmpeg. |

---

**Speaker Diarization**

| Option | Description |
|--------|-------------|
| `--diarize` | Speaker diarization (requires pyannote.audio; install via `setup.sh --diarize`) |
| `--min-speakers N` | Minimum number of speakers hint for diarization |
| `--max-speakers N` | Maximum number of speakers hint for diarization |
| `--speaker-names NAMES` | Comma-separated names to replace SPEAKER_1, SPEAKER_2 (e.g. `Alice,Bob`). Requires `--diarize` |
| `--export-speakers DIR` | Export each speaker's audio turns as separate WAV files. Requires `--diarize` and ffmpeg. |

---

**Transcript Tools**

| Option | Description |
|--------|-------------|
| `--search TERM` | Search the transcript for TERM and print matching segments with timestamps (replaces normal output) |
| `--search-fuzzy` | Enable fuzzy/approximate matching with `--search` |
| `--detect-chapters` | Auto-detect chapter breaks from silence gaps |
| `--chapter-gap SEC` | Minimum silence gap to start a new chapter (default: 8.0s) |
| `--chapters-file PATH` | Write chapter markers to this file (default: stdout after transcript) |
| `--chapter-format FMT` | `youtube` \| `text` \| `json` — chapter output format (default: `youtube`) |
| `--filter-hallucinations` | Remove common Whisper hallucinations (music markers, duplicates, etc.) |
| `--detect-language-only` | Detect language and exit — no transcription |
| `--min-confidence PROB` | Drop segments below this avg word confidence (0.0–1.0) |

---

**Batch Processing**

| Option | Description |
|--------|-------------|
| `--skip-existing` | Skip files whose output already exists |
| `--parallel N` | Number of parallel workers for batch processing (default: sequential) |
| `--retries N` | Retry failed files up to N times with exponential backoff (default: 0) |
| `--stats-file PATH` | Write JSON performance stats sidecar after transcription |
| `--output-template TMPL` | Batch output filename template (`{stem}`, `{lang}`, `{ext}`, `{model}`) |
| `--keep-temp` | Keep temp files from URL downloads (useful for re-processing without re-downloading) |
| `--burn-in OUTPUT` | Burn subtitles into the original video (single-file mode; requires ffmpeg) |

---

**RSS / Podcast**

| Option | Description |
|--------|-------------|
| `--rss URL` | Podcast RSS feed URL — extracts audio enclosures and transcribes them |
| `--rss-latest N` | Number of most-recent episodes to process (default: 5; 0 = all) |

---

**Device**

| Option | Short | Description |
|--------|-------|-------------|
| `--device DEV` | | `auto` \| `cpu` \| `cuda` (default: `auto`) |
| `--compute-type TYPE` | | `auto` \| `int8` \| `int8_float16` \| `float16` \| `float32` (default: `auto`) |
| `--threads N` | | CPU thread count for CTranslate2 (default: auto) |
| `--quiet` | `-q` | Suppress progress and status messages |
| `--log-level LEVEL` | | `debug` \| `info` \| `warning` \| `error` (default: `warning`) |

---

**Utility**

| Option | Description |
|--------|-------------|
| `--version` | Print installed faster-whisper version and exit |
| `--update` | Upgrade faster-whisper in the skill venv and exit |

## Cross-Platform Support

| Platform | GPU Accel | Auto-Install |
|----------|-----------|--------------|
| **Windows + NVIDIA** | ✅ CUDA | ✅ via winget |
| **Linux + NVIDIA** | ✅ CUDA | ❌ manual |
| **WSL2 + NVIDIA** | ✅ CUDA | ❌ manual |
| **macOS (Apple Silicon)** | ❌ CPU only | ❌ manual |
| **Windows/Linux (no GPU)** | ❌ CPU only | Windows: ✅ / Linux: ❌ |

**Notes:**
- GPU acceleration is **~20-60x faster** than CPU
- Apple Silicon Macs run on CPU but are still reasonably fast (~2-3x slower than CUDA)
- On platforms without auto-install, your agent can guide you through manual setup

### CUDA Requirements (NVIDIA GPUs)

- **Windows:** CUDA drivers auto-install with GPU drivers
- **Linux/WSL2:** Install CUDA Toolkit separately:
  ```bash
  # Ubuntu/Debian
  sudo apt install nvidia-cuda-toolkit
  
  # Check CUDA is available
  nvidia-smi
  ```

## Default Model

**distil-large-v3.5** (756MB download)

- ~6x faster than large-v3
- Within ~1% accuracy of full model
- Best balance of speed and accuracy

See `SKILL.md` for full model list and recommendations.

## Troubleshooting

### CUDA Not Detected

**Symptom:** Script says "CUDA not available — using CPU (this will be slow!)"

**Solutions:**

1. **Check NVIDIA drivers are installed:**
   ```bash
   # Windows/Linux/WSL2
   nvidia-smi
   ```
   If this fails, install/update your [NVIDIA drivers](https://www.nvidia.com/download/index.aspx)

2. **WSL2 users:** Install CUDA drivers on **Windows**, not inside WSL2
   - Follow: [NVIDIA CUDA on WSL2 Guide](https://docs.nvidia.com/cuda/wsl-user-guide/)

3. **Reinstall PyTorch with CUDA:**
   ```bash
   # Linux/macOS/WSL2
   .venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cu121
   
   # Windows
   .venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

4. **Verify CUDA is working:**
   ```bash
   # Linux/macOS/WSL2
   .venv/bin/python -c "import torch; print(torch.cuda.is_available())"
   
   # Windows
   .venv\Scripts\python -c "import torch; print(torch.cuda.is_available())"
   ```

### Out of Memory Errors

**Symptom:** `RuntimeError: CUDA out of memory` or `OutOfMemoryError`

**Solutions:**

1. **Use a smaller model:**
   ```bash
   # Try distil-medium instead of distil-large-v3.5
   ./scripts/transcribe audio.mp3 --model distil-medium.en
   ```

2. **Use int8 quantization (reduces VRAM by ~4x):**
   ```bash
   ./scripts/transcribe audio.mp3 --compute-type int8
   ```

3. **Reduce batch size:**
   ```bash
   ./scripts/transcribe audio.mp3 --batch-size 4
   ```

4. **Fall back to CPU for large files:**
   ```bash
   ./scripts/transcribe audio.mp3 --device cpu
   ```

5. **Split long audio files into smaller chunks** (5-10 min segments)

**VRAM Requirements:**
| Model | float16 | int8 |
|-------|---------|------|
| distil-large-v3.5 | ~2GB | ~1GB |
| large-v3 | ~5GB | ~2GB |
| medium | ~3GB | ~1.5GB |
| small | ~2GB | ~1GB |

### ffmpeg Not Found

**Symptom:** `FileNotFoundError: ffmpeg not found` when using `--burn-in`, `--normalize`, `--denoise`, `--channel`, or `--export-speakers`

**Note:** ffmpeg is **not required** for basic transcription — PyAV (bundled with faster-whisper) handles all standard audio decoding. You only need ffmpeg for the preprocessing and video features listed above.

**Solutions:**

1. **Windows:** Re-run setup script (auto-installs via winget)
   ```powershell
   .\setup.ps1
   ```

2. **Linux:**
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg
   
   # Fedora/RHEL
   sudo dnf install ffmpeg
   
   # Arch
   sudo pacman -S ffmpeg
   ```

3. **macOS:**
   ```bash
   brew install ffmpeg
   ```

4. **Verify installation:**
   ```bash
   ffmpeg -version
   ```

### Audio Format Issues

**Symptom:** `Error: Unsupported format` or transcription produces garbage

**Solutions:**

1. **Supported formats:** MP3, WAV, M4A, FLAC, OGG, WebM, MP4, MKV, AVI, WMA, AAC
   - Most common audio and video formats are supported via PyAV

2. **Convert problematic formats:**
   ```bash
   ffmpeg -i input.xyz -ar 16000 output.wav
   ```

3. **Check audio isn't corrupted:**
   ```bash
   ffmpeg -i audio.mp3 -f null -
   ```

### Model Download Fails

**Symptom:** `HTTPError`, `ConnectionError`, or timeout during first run

**Solutions:**

1. **Check internet connection**

2. **Retry with increased timeout:**
   - Models download automatically on first use
   - Download sizes: 75MB (tiny) to 3GB (large-v3)

3. **Use a VPN if Hugging Face is blocked** in your region

4. **Manual download:**
   ```python
   from faster_whisper import WhisperModel
   model = WhisperModel("distil-large-v3.5", device="cpu")
   ```

### Very Slow Transcription

**Symptom:** Transcription takes longer than the audio duration

**Expected speeds:**
- **GPU (CUDA):** ~20-30x realtime (30 min audio → ~1-2 min)
- **Apple Silicon (CPU):** ~2-5x realtime (30 min audio → ~6-15 min)
- **Intel CPU:** ~0.5-1x realtime (30 min audio → 30-60 min)

**Solutions:**

1. **Ensure GPU is being used:**
   ```bash
   # Look for "Loading model: ... (cuda, float16) on NVIDIA ..."
   ./scripts/transcribe audio.mp3
   ```

2. **Use a smaller/distilled model:**
   ```bash
   ./scripts/transcribe audio.mp3 --model distil-small.en
   ```

3. **Specify language (skips auto-detection):**
   ```bash
   ./scripts/transcribe audio.mp3 --language en
   ```

4. **Reduce beam size:**
   ```bash
   ./scripts/transcribe audio.mp3 --beam-size 1
   ```

### Python Version Issues

**Symptom:** `SyntaxError` or `ImportError` during setup

**Solutions:**

1. **Requires Python 3.10 or newer:**
   ```bash
   python --version  # or python3 --version
   ```

2. **Windows:** Setup script auto-installs Python 3.12 via winget

3. **Linux/macOS:** Install Python 3.10+:
   ```bash
   # Ubuntu
   sudo apt install python3.12 python3.12-venv
   
   # macOS
   brew install python@3.12
   ```

### Still Having Issues?

1. **Run the system check:** `./setup.sh --check` — verifies GPU, Python, ffmpeg, venv, yt-dlp, and pyannote
2. **Check the logs:** Run without `--quiet` to see detailed error messages
3. **Ask your agent:** Paste the error — it can usually diagnose faster-whisper or installation issues
4. **Open an issue:** [GitHub Issues](https://github.com/ThePlasmak/faster-whisper/issues)
5. **Include:**
   - Platform (Windows/Linux/macOS/WSL2)
   - GPU model (if any)
   - Python version
   - Full error message

## See Also

**[parakeet](https://github.com/ThePlasmak/parakeet)** — If you have an NVIDIA GPU and want the absolute fastest transcription, parakeet uses NVIDIA's Parakeet TDT model (NeMo) and hits ~3380× realtime on GPU — roughly 150× faster than faster-whisper on the same hardware. Trade-offs: fewer output formats, 25 European languages only (vs 99+), Linux/WSL2 only, and no diarization or advanced features.

## References

- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [Distil-Whisper Paper](https://arxiv.org/abs/2311.00430)
- [OpenAI Whisper Models](https://github.com/openai/whisper#available-models-and-languages)
- [HuggingFace Models](https://huggingface.co/collections/Systran/faster-whisper)
- [pyannote.audio](https://github.com/pyannote/pyannote-audio) (diarization)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (URL/YouTube download)
