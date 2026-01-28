# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-28

### Added
- Initial release with cross-platform support (Windows, Linux, macOS, WSL2)
- Automatic setup scripts with dependency detection
  - Windows: Auto-installs Python & ffmpeg via winget
  - Linux/macOS/WSL2: Manual prerequisite installation
- GPU auto-detection and CUDA support
  - Automatic PyTorch CUDA installation when NVIDIA GPU detected
  - ~50-100x speedup over CPU transcription
- Multiple model support
  - Standard models (tiny, base, small, medium, large)
  - Distilled models (6x faster with <1% accuracy loss)
  - Default: distil-large-v3 (best speed/accuracy balance)
- Word-level timestamps with `--word-timestamps`
- Voice activity detection (VAD) with `--vad`
- JSON output format with `--json`
- Language auto-detection or manual specification
- Beam search size control
- Cross-platform CLI wrappers
  - Bash script for Linux/macOS/WSL2
  - PowerShell script for Windows
  - Batch script for Windows compatibility
- Comprehensive documentation
  - README with setup, usage, and platform support
  - SKILL.md for Moltbot integration
  - CLI help text and examples
