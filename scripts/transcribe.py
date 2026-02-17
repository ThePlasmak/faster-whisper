#!/usr/bin/env python3
"""
faster-whisper transcription CLI
High-performance speech-to-text using CTranslate2 backend with batched inference.

Features:
- Multiple output formats: text, JSON, SRT, VTT
- URL/YouTube input via yt-dlp
- Speaker diarization (optional, requires pyannote.audio)
- Batch processing with glob patterns and directories
- Initial prompt for domain-specific terminology
- Confidence-based segment filtering
- Performance statistics
"""

import sys
import os
import json
import time
import glob
import argparse
import tempfile
import subprocess
import shutil
from pathlib import Path

try:
    from faster_whisper import WhisperModel, BatchedInferencePipeline
except ImportError:
    print("Error: faster-whisper not installed", file=sys.stderr)
    print("Run setup: ./setup.sh", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def check_cuda_available():
    """Check if CUDA is available and return device info."""
    try:
        import torch
        if torch.cuda.is_available():
            return True, torch.cuda.get_device_name(0)
        return False, None
    except ImportError:
        return False, None


def format_ts_srt(seconds):
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_ts_vtt(seconds):
    """Format seconds as VTT timestamp: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_duration(seconds):
    """Format duration as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m}m{s:.0f}s"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h}h{m}m"


def is_url(path):
    """Check if the input looks like a URL."""
    return path.startswith(("http://", "https://", "www."))


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def to_srt(segments):
    """Format segments as SRT subtitle content."""
    lines = []
    for i, seg in enumerate(segments, 1):
        text = seg["text"].strip()
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"
        lines.append(str(i))
        lines.append(f"{format_ts_srt(seg['start'])} --> {format_ts_srt(seg['end'])}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def to_vtt(segments):
    """Format segments as WebVTT subtitle content."""
    lines = ["WEBVTT", ""]
    for i, seg in enumerate(segments, 1):
        text = seg["text"].strip()
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"
        lines.append(str(i))
        lines.append(f"{format_ts_vtt(seg['start'])} --> {format_ts_vtt(seg['end'])}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def to_text(segments):
    """Format segments as plain text, with speaker labels if present."""
    has_speakers = any(seg.get("speaker") for seg in segments)
    if not has_speakers:
        return "".join(seg["text"] for seg in segments).strip()

    lines = []
    current_speaker = None
    for seg in segments:
        sp = seg.get("speaker")
        if sp and sp != current_speaker:
            current_speaker = sp
            lines.append(f"\n[{sp}]")
        lines.append(seg["text"])
    return "".join(lines).strip()


# ---------------------------------------------------------------------------
# URL download
# ---------------------------------------------------------------------------

def download_url(url, quiet=False):
    """Download audio from URL using yt-dlp. Returns (audio_path, tmpdir)."""
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        pipx_path = Path.home() / ".local/share/pipx/venvs/yt-dlp/bin/yt-dlp"
        if pipx_path.exists():
            ytdlp = str(pipx_path)
        else:
            print("Error: yt-dlp not found. Install with: pipx install yt-dlp", file=sys.stderr)
            sys.exit(1)

    tmpdir = tempfile.mkdtemp(prefix="faster-whisper-")
    out_tmpl = os.path.join(tmpdir, "audio.%(ext)s")

    cmd = [ytdlp, "-x", "--audio-format", "mp3", "-o", out_tmpl, "--no-playlist"]
    if quiet:
        cmd.append("-q")
    cmd.append(url)

    if not quiet:
        print("⬇️  Downloading audio from URL...", file=sys.stderr)

    try:
        subprocess.run(cmd, check=True, capture_output=quiet)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading URL: {e}", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    files = list(Path(tmpdir).glob("audio.*"))
    if not files:
        print("Error: No audio file downloaded", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    return str(files[0]), tmpdir


# ---------------------------------------------------------------------------
# Speaker diarization
# ---------------------------------------------------------------------------

def run_diarization(audio_path, segments, quiet=False):
    """Assign speaker labels to segments using pyannote.audio."""
    try:
        from pyannote.audio import Pipeline as PyannotePipeline
    except ImportError:
        print(
            "Error: pyannote.audio not installed.\n"
            "  Install: ./setup.sh --diarize\n"
            "  Or:      pip install pyannote.audio",
            file=sys.stderr,
        )
        sys.exit(1)

    if not quiet:
        print("🔊 Running speaker diarization...", file=sys.stderr)

    try:
        pipeline = PyannotePipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1"
        )
    except Exception as e:
        print(f"Error loading diarization model: {e}", file=sys.stderr)
        print(
            "  Ensure you have a HuggingFace token at ~/.cache/huggingface/token\n"
            "  and accepted: https://hf.co/pyannote/speaker-diarization-3.1",
            file=sys.stderr,
        )
        sys.exit(1)

    # Move to GPU if available
    try:
        import torch
        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))
    except Exception:
        pass

    # pyannote works best with WAV; convert compressed formats to avoid
    # sample-count mismatches (known issue with MP3/OGG)
    diarize_path = audio_path
    tmp_wav = None
    if not audio_path.lower().endswith(".wav"):
        tmp_wav = audio_path + ".diarize.wav"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", tmp_wav],
                check=True, capture_output=True,
            )
            diarize_path = tmp_wav
        except Exception:
            # Fall back to original file if conversion fails
            tmp_wav = None

    try:
        diarize_result = pipeline(diarize_path)
    finally:
        if tmp_wav and os.path.exists(tmp_wav):
            os.remove(tmp_wav)

    # pyannote 4.x returns DiarizeOutput with .speaker_diarization attribute;
    # pyannote 3.x returns an Annotation directly
    if hasattr(diarize_result, "speaker_diarization"):
        annotation = diarize_result.speaker_diarization
    else:
        annotation = diarize_result

    # Build speaker timeline
    timeline = [
        {"start": turn.start, "end": turn.end, "speaker": speaker}
        for turn, _, speaker in annotation.itertracks(yield_label=True)
    ]

    def speaker_at(t):
        """Find the speaker at a given timestamp by max overlap with a point."""
        best, best_overlap = None, 0
        for tl in timeline:
            if tl["start"] <= t <= tl["end"]:
                overlap = min(tl["end"], t + 0.01) - max(tl["start"], t)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best = tl["speaker"]
        return best

    # Collect all words across segments for word-level speaker assignment
    all_words = []
    for seg in segments:
        if seg.get("words"):
            all_words.extend(seg["words"])

    if all_words:
        # Word-level diarization: assign speaker to each word, then regroup
        # into speaker-homogeneous segments
        for w in all_words:
            mid = (w["start"] + w["end"]) / 2
            w["speaker"] = speaker_at(mid)

        # Group consecutive words by speaker into new segments
        new_segments = []
        current_speaker = None
        current_words = []

        def flush_group():
            if not current_words:
                return
            new_segments.append({
                "start": current_words[0]["start"],
                "end": current_words[-1]["end"],
                "text": "".join(w["word"] for w in current_words),
                "speaker": current_speaker,
                "words": list(current_words),
            })

        for w in all_words:
            sp = w.get("speaker")
            if sp != current_speaker and current_words:
                flush_group()
                current_words = []
            current_speaker = sp
            current_words.append(w)
        flush_group()

        segments = new_segments
    else:
        # No word-level data: fall back to segment-level assignment
        for seg in segments:
            mid = (seg["start"] + seg["end"]) / 2
            seg["speaker"] = speaker_at(mid)

    # Rename to SPEAKER_1, SPEAKER_2, ... in order of appearance
    seen = {}
    for seg in segments:
        raw = seg.get("speaker")
        if raw and raw not in seen:
            seen[raw] = f"SPEAKER_{len(seen) + 1}"
        if raw:
            seg["speaker"] = seen[raw]

    if not quiet:
        print(f"   Found {len(seen)} speaker(s)", file=sys.stderr)

    return segments, list(seen.values())


# ---------------------------------------------------------------------------
# File resolution
# ---------------------------------------------------------------------------

AUDIO_EXTS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm",
    ".mp4", ".mkv", ".avi", ".wma", ".aac",
}


def resolve_inputs(inputs):
    """Expand globs, directories, and URLs into a flat list of audio paths."""
    files = []
    for inp in inputs:
        if is_url(inp):
            files.append(inp)
            continue
        expanded = sorted(glob.glob(inp, recursive=True)) or [inp]
        for p_str in expanded:
            p = Path(p_str)
            if p.is_dir():
                files.extend(
                    str(f) for f in sorted(p.iterdir())
                    if f.is_file() and f.suffix.lower() in AUDIO_EXTS
                )
            elif p.is_file():
                files.append(str(p))
            else:
                print(f"Warning: not found: {inp}", file=sys.stderr)
    return files


# ---------------------------------------------------------------------------
# Core transcription
# ---------------------------------------------------------------------------

def transcribe_file(audio_path, pipeline, args):
    """Transcribe a single audio file. Returns result dict."""
    t0 = time.time()

    need_words = (
        args.word_timestamps
        or args.min_confidence is not None
        or args.diarize  # word-level needed for accurate speaker assignment
    )

    kw = dict(
        language=args.language,
        beam_size=args.beam_size,
        word_timestamps=need_words,
        vad_filter=not args.no_vad,
        hotwords=args.hotwords,
        initial_prompt=args.initial_prompt,
    )
    if not args.no_batch:
        kw["batch_size"] = args.batch_size

    segments_iter, info = pipeline.transcribe(str(audio_path), **kw)

    segments = []
    full_text = ""

    for seg in segments_iter:
        # Confidence filter (needs word-level probabilities)
        if args.min_confidence is not None and seg.words:
            avg = sum(w.probability for w in seg.words) / len(seg.words)
            if avg < args.min_confidence:
                continue

        full_text += seg.text
        seg_data = {"start": seg.start, "end": seg.end, "text": seg.text}

        if need_words and seg.words:
            seg_data["words"] = [
                {
                    "word": w.word,
                    "start": w.start,
                    "end": w.end,
                    "probability": w.probability,
                }
                for w in seg.words
            ]

        segments.append(seg_data)

    # Diarize after transcription
    speakers = None
    if args.diarize:
        segments, speakers = run_diarization(
            str(audio_path), segments, quiet=args.quiet
        )

    elapsed = time.time() - t0
    dur = info.duration
    rt = round(dur / elapsed, 1) if elapsed > 0 else 0

    result = {
        "file": Path(audio_path).name,
        "text": full_text.strip(),
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": dur,
        "segments": segments,
        "stats": {
            "processing_time": round(elapsed, 2),
            "realtime_factor": rt,
        },
    }
    if speakers:
        result["speakers"] = speakers

    if not args.quiet:
        print(
            f"✅ {result['file']}: {format_duration(dur)} in "
            f"{format_duration(elapsed)} ({rt}× realtime)",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

EXT_MAP = {"text": ".txt", "json": ".json", "srt": ".srt", "vtt": ".vtt"}


def format_result(result, fmt):
    """Render a result dict in the requested format."""
    if fmt == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    if fmt == "srt":
        return to_srt(result["segments"])
    if fmt == "vtt":
        return to_vtt(result["segments"])
    return to_text(result["segments"])


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Transcribe audio with faster-whisper",
        epilog=(
            "examples:\n"
            "  %(prog)s audio.mp3\n"
            "  %(prog)s audio.mp3 --format srt -o subtitles.srt\n"
            "  %(prog)s https://youtube.com/watch?v=... --language en\n"
            "  %(prog)s *.mp3 --skip-existing -o ./transcripts/\n"
            "  %(prog)s meeting.wav --diarize --format vtt\n"
            "  %(prog)s lecture.mp3 --initial-prompt 'Kubernetes, gRPC'\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Positional ---
    p.add_argument(
        "audio", nargs="+", metavar="AUDIO",
        help="Audio file(s), directory, glob pattern, or URL",
    )

    # --- Model & language ---
    p.add_argument(
        "-m", "--model", default="distil-large-v3.5",
        help="Whisper model (default: distil-large-v3.5)",
    )
    p.add_argument(
        "-l", "--language", default=None,
        help="Language code, e.g. en, es, fr (auto-detects if omitted)",
    )
    p.add_argument(
        "--initial-prompt", default=None, metavar="TEXT",
        help="Prompt to condition the model (terminology, formatting hints)",
    )
    p.add_argument(
        "--hotwords", default=None, metavar="WORDS",
        help="Hotwords to boost recognition (space-separated)",
    )

    # --- Output format ---
    p.add_argument(
        "-f", "--format", default="text",
        choices=["text", "json", "srt", "vtt"],
        help="Output format (default: text)",
    )
    p.add_argument(
        "--word-timestamps", action="store_true",
        help="Include word-level timestamps (auto-enabled for --diarize)",
    )
    p.add_argument(
        "-o", "--output", default=None, metavar="PATH",
        help="Output file or directory (directory for batch mode)",
    )

    # --- Inference tuning ---
    p.add_argument(
        "--beam-size", type=int, default=5, metavar="N",
        help="Beam search size (default: 5)",
    )
    p.add_argument(
        "--batch-size", type=int, default=8, metavar="N",
        help="Batch size for batched inference (default: 8; reduce if OOM)",
    )
    p.add_argument("--no-vad", action="store_true",
                    help="Disable voice activity detection")
    p.add_argument("--no-batch", action="store_true",
                    help="Disable batched inference (use standard WhisperModel)")

    # --- Advanced features ---
    p.add_argument(
        "--diarize", action="store_true",
        help="Speaker diarization (requires pyannote.audio; install via setup.sh --diarize)",
    )
    p.add_argument(
        "--min-confidence", type=float, default=None, metavar="PROB",
        help="Drop segments below this avg word confidence (0.0–1.0)",
    )
    p.add_argument(
        "--skip-existing", action="store_true",
        help="Skip files whose output already exists (batch mode)",
    )

    # --- Device ---
    p.add_argument(
        "--device", default="auto", choices=["auto", "cpu", "cuda"],
        help="Compute device (default: auto)",
    )
    p.add_argument(
        "--compute-type", default="auto",
        choices=["auto", "int8", "float16", "float32"],
        help="Quantization (default: auto)",
    )
    p.add_argument(
        "-q", "--quiet", action="store_true",
        help="Suppress progress messages",
    )

    # --- Backward compat (hidden) ---
    p.add_argument("-j", "--json", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--vad", action="store_true", help=argparse.SUPPRESS)

    args = p.parse_args()
    if args.json:
        args.format = "json"

    # ---- Resolve inputs ----
    temp_dirs = []
    audio_files = []
    for inp in args.audio:
        if is_url(inp):
            path, td = download_url(inp, quiet=args.quiet)
            audio_files.append(path)
            temp_dirs.append(td)
        else:
            audio_files.extend(resolve_inputs([inp]))

    if not audio_files:
        print("Error: No audio files found", file=sys.stderr)
        sys.exit(1)

    is_batch = len(audio_files) > 1

    # ---- Device setup ----
    device = args.device
    compute_type = args.compute_type
    cuda_ok, gpu_name = check_cuda_available()

    if device == "auto":
        device = "cuda" if cuda_ok else "cpu"
        if device == "cpu" and not args.quiet:
            print("⚠️  CUDA not available — using CPU (this will be slow!)", file=sys.stderr)
            print("   To enable GPU: pip install torch --index-url https://download.pytorch.org/whl/cu121", file=sys.stderr)

    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"

    use_batched = not args.no_batch

    if not args.quiet:
        mode = f"batched (bs={args.batch_size})" if use_batched else "standard"
        gpu_str = f" on {gpu_name}" if device == "cuda" and gpu_name else ""
        print(f"🎙️  {args.model} ({device}/{compute_type}){gpu_str} [{mode}]", file=sys.stderr)
        if is_batch:
            print(f"📁 {len(audio_files)} files queued", file=sys.stderr)

    # ---- Load model ----
    try:
        model = WhisperModel(args.model, device=device, compute_type=compute_type)
        pipe = BatchedInferencePipeline(model) if use_batched else model
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        sys.exit(1)

    # ---- Transcribe ----
    results = []
    total_audio = 0
    wall_start = time.time()

    for audio_path in audio_files:
        name = Path(audio_path).name

        # Skip-existing check
        if args.skip_existing and args.output:
            out_dir = Path(args.output)
            if out_dir.is_dir():
                target = out_dir / (Path(audio_path).stem + EXT_MAP.get(args.format, ".txt"))
                if target.exists():
                    if not args.quiet:
                        print(f"⏭️  Skip (exists): {name}", file=sys.stderr)
                    continue

        if not args.quiet and is_batch:
            print(f"▶️  {name}", file=sys.stderr)

        try:
            r = transcribe_file(audio_path, pipe, args)
            results.append(r)
            total_audio += r["duration"]
        except Exception as e:
            print(f"Error: {name}: {e}", file=sys.stderr)
            if not is_batch:
                sys.exit(1)

    # Cleanup temp dirs
    for td in temp_dirs:
        shutil.rmtree(td, ignore_errors=True)

    if not results:
        if args.skip_existing:
            if not args.quiet:
                print("All files already transcribed (--skip-existing)", file=sys.stderr)
            sys.exit(0)
        print("Error: No files transcribed", file=sys.stderr)
        sys.exit(1)

    # ---- Write output ----
    for r in results:
        output = format_result(r, args.format)

        if args.output:
            out_path = Path(args.output)
            if out_path.is_dir() or (is_batch and not out_path.suffix):
                out_path.mkdir(parents=True, exist_ok=True)
                dest = out_path / (Path(r["file"]).stem + EXT_MAP.get(args.format, ".txt"))
            else:
                dest = out_path
            dest.write_text(output, encoding="utf-8")
            if not args.quiet:
                print(f"💾 {dest}", file=sys.stderr)
        else:
            if is_batch and args.format == "text":
                print(f"\n=== {r['file']} ===")
            print(output)

    # Batch summary
    if is_batch and not args.quiet:
        wall = time.time() - wall_start
        rt = total_audio / wall if wall > 0 else 0
        print(
            f"\n📊 Done: {len(results)} files, {format_duration(total_audio)} audio "
            f"in {format_duration(wall)} ({rt:.1f}× realtime)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
