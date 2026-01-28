# faster-whisper

A Moltbot skill for speech-to-text that uses faster-whisper — a CTranslate2 reimplementation of OpenAI's Whisper that's ~4-6x faster with identical accuracy.

## Features

- **~4-6x faster** than OpenAI's original Whisper (same model weights, CTranslate2 backend)
- **~20x realtime** with GPU — transcribe 10 min of audio in ~30 sec
- **Distilled models** available (~6x faster again with <1% WER loss)
- **Word-level timestamps**
- **Voice activity detection (VAD)** — removes silence automatically
- **Multilingual support** (100+ languages)
- **Quantization** for CPU efficiency
- **GPU acceleration** (NVIDIA CUDA)

## Installation

### Option 1: Install from MoltHub

An easy way to install this skill into Moltbot:

```bash
clawdhub install faster-whisper
```

This downloads and installs the skill into your default skills directory (`~/clawd/moltbot/workspace/skills/` or similar).

### Option 2: Download from GitHub Releases

1. Go to [Releases](https://github.com/ThePlasmak/faster-whisper/releases)
2. Download the latest `faster-whisper-X.X.X.zip`
3. Extract it to your Moltbot skills folder:
   - **Default location**: `~/clawd/moltbot/workspace/skills/faster-whisper`
   - Or wherever your Moltbot workspace is configured

```bash
# Example
cd ~/clawd/moltbot/workspace/skills/
unzip ~/Downloads/faster-whisper-1.0.1.zip -d faster-whisper
```

**Note:** The release zip excludes repository files (CHANGELOG, LICENSE, README) and only contains the skill itself — this keeps things lightweight.

## Setup

### Using with Moltbot

If you're using Moltbot, it can guide you through the installation automatically.

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
- Use the GPU if available
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
- GPU acceleration is **~20-60x faster** than CPU
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
   # Try distil-medium instead of distil-large-v3
   ./scripts/transcribe audio.mp3 --model distil-medium.en
   ```

2. **Use int8 quantization (reduces VRAM by ~4x):**
   ```bash
   ./scripts/transcribe audio.mp3 --compute-type int8
   ```

3. **Fall back to CPU for large files:**
   ```bash
   ./scripts/transcribe audio.mp3 --device cpu
   ```

4. **Split long audio files into smaller chunks** (5-10 min segments)

**VRAM Requirements:**
| Model | float16 | int8 |
|-------|---------|------|
| distil-large-v3 | ~2GB | ~1GB |
| large-v3 | ~5GB | ~2GB |
| medium | ~3GB | ~1.5GB |
| small | ~2GB | ~1GB |

### ffmpeg Not Found

**Symptom:** `FileNotFoundError: ffmpeg not found`

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
   model = WhisperModel("distil-large-v3", device="cpu")
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

### Audio Format Issues

**Symptom:** `Error: Unsupported format` or transcription produces garbage

**Solutions:**

1. **Supported formats:** MP3, WAV, M4A, FLAC, OGG, WebM
   - Most common formats work via ffmpeg

2. **Convert problematic formats:**
   ```bash
   ffmpeg -i input.xyz -ar 16000 output.mp3
   ```

3. **Check audio isn't corrupted:**
   ```bash
   ffmpeg -i audio.mp3 -f null -
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

1. **Check the logs:** Run without `--quiet` to see detailed error messages
2. **Ask Moltbot:** Paste the error — it can usually diagnose faster-whisper or installation issues
3. **Open an issue:** [GitHub Issues](https://github.com/ThePlasmak/faster-whisper/issues)
4. **Include:**
   - Platform (Windows/Linux/macOS/WSL2)
   - GPU model (if any)
   - Python version
   - Full error message

## References

- [faster-whisper GitHub](https://github.com/SYSTRAN/faster-whisper)
- [Distil-Whisper Paper](https://arxiv.org/abs/2311.00430)
- [OpenAI Whisper Models](https://github.com/openai/whisper#available-models-and-languages)
