# Changelog

All notable changes to this project will be documented in this file.

## [1.10.0] - 2026-02-18

- Added ASS/SSA subtitle format (`--format ass`) — Advanced SubStation Alpha compatible with Aegisub, VLC, mpv, MPC-HC, and most video editors
- Added `setup.sh --check` — quick system diagnostic verifying GPU, CUDA, Python, ffmpeg, faster-whisper version, yt-dlp, pyannote, and HuggingFace token
- Documented pre-conversion tip: 16kHz mono WAV pre-convert for repeated processing workflows
- Clarified faster-whisper vs whisperx: this skill covers all whisperx use cases (diarization, word timestamps, SRT/VTT/ASS)

## [1.5.0] - 2026-02-18

- Added VAD tuning parameters (--vad-threshold, --vad-neg-threshold, --min-speech-duration, --max-speech-duration, --min-silence-duration, --speech-pad)
- Added temperature control (--temperature) for hallucination-prone audio
- Added no-speech threshold (--no-speech-threshold) to filter noise segments
- Added min/max speaker hints for diarization (--min-speakers, --max-speakers)
- Added TSV output format for OpenAI Whisper interoperability
- Added --update flag to upgrade faster-whisper without full re-setup
- Added --version flag to show installed version
- Added --hf-token for direct HuggingFace token passing
- Added --max-words-per-line for better subtitle readability
- Added --revision for pinning specific model revisions
- Added --threads for CPU thread control
- Added beam search tuning (--best-of, --patience)
- Added anti-repetition controls (--repetition-penalty, --no-repeat-ngram-size)
- Bumped minimum faster-whisper requirement to >=1.2.1

## [1.0.1] - 2026-01-28

Remove install metadata (as ClawdHub's install section is confusing); add python3 to required binaries

## [1.0.0] - 2026-01-28

Initial release: Local speech-to-text using faster-whisper with 4-6x speed boost over OpenAI Whisper. GPU acceleration enables ~20x realtime transcription. Auto-setup scripts for Windows/Linux/macOS with CUDA detection. Supports distilled models for 6x additional speedup.
