import shutil
import subprocess
import os

from core.exceptions import VideoProcessingError


# ── helpers ──────────────────────────────────────────────────────────────────

def _run(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="ignore") if e.stderr else ""
        raise VideoProcessingError(f"ffmpeg error:\n{stderr}") from e


def get_duration(path: str) -> float:
    """Returns media file duration in seconds."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            capture_output=True, text=True, check=True,
        )
        return float(r.stdout.strip())
    except Exception as e:
        raise VideoProcessingError(f"ffprobe: {e}") from e


# ── operations ───────────────────────────────────────────────────────────────

def extract_audio(video_path: str, audio_path: str) -> None:
    """Extracts audio from video in MP3 format (16 kHz, mono)."""
    _run([
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "mp3", "-ar", "16000", "-ac", "1",
        audio_path, "-y", "-loglevel", "error",
    ])


def fit_audio_to_video(audio_path: str, video_dur: float, output_path: str) -> None:
    """
    Speeds up the audio so that it fits within the video's duration.
    Maximum speedup: 2x (limit of the atempo filter).
    """
    audio_dur = get_duration(audio_path)

    if audio_dur <= video_dur * 1.02:       # вже вміщається — без змін
        shutil.copy(audio_path, output_path)
        return

    ratio = min(round(audio_dur / video_dur, 4), 2.0)
    _run([
        "ffmpeg", "-i", audio_path,
        "-filter:a", f"atempo={ratio}",
        output_path, "-y", "-loglevel", "error",
    ])


def merge(video_path: str, audio_path: str, output_path: str) -> None:
    """Replaces the video's audio track with a new one."""
    _run([
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        output_path, "-y", "-loglevel", "error",
    ])

def fit_segment(audio_path: str, target_dur: float, output_path: str) -> None:
    """Adjusts a single segment to fit the required slot duration."""
    try:
        dur = get_duration(audio_path)
    except VideoProcessingError:
        dur = 0.0

    if dur <= 0.05:
        _run([
            "ffmpeg", "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=mono",
            "-t", str(max(target_dur, 0.1)),
            output_path, "-y", "-loglevel", "error",
        ])
        return

    if dur <= target_dur * 1.05:
        _run([
            "ffmpeg", "-i", audio_path,
            "-af", f"apad=whole_dur={target_dur}",
            output_path, "-y", "-loglevel", "error",
        ])
    else:
        ratio = min(round(dur / target_dur, 4), 2.0)
        _run([
            "ffmpeg", "-i", audio_path,
            "-filter:a", f"atempo={ratio}",
            "-t", str(target_dur),
            output_path, "-y", "-loglevel", "error",
        ])


def build_sync_audio(
    segments: list[tuple[float, float, str]],  # (start, end, audio_file)
    video_duration: float,
    tmp_dir: str,
    output_path: str,
) -> None:
    """
   Adjusts a single segment to fit the required slot duration.
    """
    fitted_files: list[tuple[float, str]] = []

    for i, (start, end, seg_audio) in enumerate(segments):
        slot    = max(end - start, 0.2)
        fit_out = os.path.join(tmp_dir, f"fit_{i}.mp3")
        fit_segment(seg_audio, slot, fit_out)
        fitted_files.append((start, fit_out))

    inputs:  list[str] = []
    filters: list[str] = []

    for i, (start, fit_path) in enumerate(fitted_files):
        inputs  += ["-i", fit_path]
        delay_ms = int(start * 1000)
        filters.append(f"[{i}:a]adelay={delay_ms}|{delay_ms}[s{i}]")

    n   = len(fitted_files)
    mix = "".join(f"[s{i}]" for i in range(n))
    filters.append(f"{mix}amix=inputs={n}:normalize=0:dropout_transition=0[out]")

    _run([
        "ffmpeg",
        *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[out]",
        "-t", str(video_duration),
        "-ar", "44100",
        "-ac", "1",
        output_path, "-y", "-loglevel", "error",
    ])

def mix_voice_with_background(
    voice_path: str,
    background_path: str,
    output_path: str,
    bg_volume: float = 0.75,
) -> None:
    """
    Assembles the final audio track: each segment
    is placed exactly at its own timestamp using adelay.
    """
    _run([
        "ffmpeg",
        "-i", background_path,
        "-i", voice_path,
        "-filter_complex",
        f"[0:a]volume={bg_volume}[bg];"
        f"[1:a]volume=1.0[v];"
        f"[bg][v]amix=inputs=2:normalize=0:dropout_transition=0[out]",
        "-map", "[out]",
        "-ar", "44100",
        "-ac", "2",
        output_path, "-y", "-loglevel", "error",
    ])