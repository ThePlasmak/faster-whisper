# faster-whisper

Local speech-to-text using faster-whisper — same accuracy as OpenAI Whisper, but ~6x faster with GPU acceleration.

## Features

- **~6x faster** than OpenAI's original Whisper
- **Same accuracy** (uses same model weights)
- **Distilled models** available (~6x faster again with <1% WER loss)
- **Word-level timestamps**
- **Voice activity detection (VAD)** — removes silence automatically
- **Multilingual support** (100+ languages)
- **Quantization** for CPU efficiency
- **GPU acceleration** (NVIDIA CUDA)

## Setup

### Using with Moltbot

If you're using Moltbot, it can guide you through installation automatically.

**What Moltbot does:**

- Detects your platform (Windows/Linux/macOS/WSL2)
- Checks for Python, ffmpeg, and GPU drivers
- Runs the appropriate setup script for you

### Standalone CLI Setup

If you want to use the transcription scripts directly without Moltbot:

**Windows (Native):**
```powershell
.\setup.ps1   # Auto-installs Python & ffmpeg via winget if needed
```

**Linux / macOS / WSL2:**
```bash
./setup.sh
```

**What it installs:**
- Python 3.10+ (if missing)
- ffmpeg (audio processing)
- faster-whisper + dependencies
- CUDA support (if NVIDIA GPU detected)

## How to Use

### With Moltbot

Just ask in natural language:

```
"Transcribe this audio file" (with file attached)
"Transcribe interview.mp3 with word timestamps"
"Transcribe this in Spanish"
"Transcribe this and save as JSON"
```

Moltbot will:
- Pick the right model for your needs
- Use GPU if available
- Handle errors and suggest fixes
- Return formatted results

### Standalone CLI

Run the transcription script directly:

**Linux / macOS / WSL2:**
```bash
./scripts/transcribe audio.mp3
./scripts/transcribe audio.mp3 --word-timestamps --json
```

**Windows:**
```powershell
.\scripts\transcribe.cmd audio.mp3
.\scripts\transcribe.cmd audio.mp3 --word-timestamps --json
```

#### CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--model` | `-m` | Model name (default: `distil-large-v3`) |
| `--language` | `-l` | Language code (e.g., `en`, `es`, `fr`) — auto-detects if omitted |
| `--word-timestamps` | | Include word-level timestamps |
| `--beam-size` | | Beam search size (default: 5, higher = more accurate but slower) |
| `--vad` | | Enable voice activity detection (removes silence) |
| `--json` | `-j` | Output as JSON |
| `--output` | `-o` | Save transcript to file |
| `--device` | | `cpu` or `cuda` (auto-detected) |
| `--compute-type` | | `int8`, `float16`, `float32` (auto-optimized) |
| `--quiet` | `-q` | Suppress progress messages |

#### CLI Examples

```bash
# Basic transcription
./scripts/transcribe interview.mp3

# Specify language (faster than auto-detect)
./scripts/transcribe podcast.mp3 --language en

# High-accuracy with word timestamps
./scripts/transcribe lecture.wav --model large-v3-turbo --word-timestamps

# JSON output saved to file
./scripts/transcribe meeting.m4a --json --output meeting.json

# Fast English-only transcription
./scripts/transcribe audio.mp3 --model distil-medium.en --language en

# Remove silence with VAD
./scripts/transcribe audio.mp3 --vad
```

## Cross-Platform Support

| Platform | GPU Accel | Auto-Install |
|----------|-----------|--------------|
| **Windows + NVIDIA** | ✅ CUDA | ✅ via winget |
| **Linux + NVIDIA** | ✅ CUDA | ❌ manual |
| **WSL2 + NVIDIA** | ✅ CUDA | ❌ manual |
| **macOS (Apple Silicon)** | ❌ CPU only | ❌ manual |
| **Windows/Linux (no GPU)** | ❌ CPU only | Windows: ✅ / Linux: ❌ |

**Notes:**
- GPU acceleration makes transcription **~50-100x faster** than CPU
- Apple Silicon Macs run on CPU but are still reasonably fast (~2-3x slower than CUDA)
- On platforms without auto-install, Moltbot can guide you through manual setup

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

**distil-large-v3** (756MB download)

- 6x faster than large-v3
- Within 1% accuracy of full model
- Best balance of speed and accuracy

See `SKILL.md` for full model list and recommendations.

## References

- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [Distil-Whisper Paper](https://arxiv.org/abs/2311.00430)
- [OpenAI Whisper Models](https://github.com/openai/whisper#available-models-and-languages)
