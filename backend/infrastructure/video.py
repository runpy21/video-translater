import shutil
import subprocess
import os
import logging
logger = logging.getLogger(__name__)

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

def fit_segment(
    audio_path: str,
    target_dur: float,
    output_path: str,
    max_speed: float = 1.5,
) -> float:
    """
    Adaptively fit audio into a time budget without truncating speech.

    Returns the actual output duration.
    If the segment cannot fit at an acceptable speed,
    preserve its full audio and allow it to overflow.
    """
    dur = get_duration(audio_path)

    if dur <= 0.05:
        _run([
            "ffmpeg", "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=mono",
            "-t", str(max(target_dur, 0.1)),
            "-c:a", "libmp3lame",
            output_path, "-y", "-loglevel", "error",
        ])
        return max(target_dur, 0.1)

    if target_dur <= 0:
        shutil.copy(audio_path, output_path)
        return dur

    # Speed up only as much as necessary, up to max_speed.
    speed = min(dur / target_dur, max_speed)

    if speed <= 1.02:
        shutil.copy(audio_path, output_path)
    else:
        _run([
            "ffmpeg", "-i", audio_path,
            "-filter:a", f"atempo={speed:.4f}",
            "-c:a", "libmp3lame",
            output_path, "-y", "-loglevel", "error",
        ])

    actual_dur = get_duration(output_path)

    if actual_dur > target_dur + 0.05:
        logger.warning(
            "Speech overflow: %.2fs audio in %.2fs budget "
            "(%.2fs overflow)",
            actual_dur,
            target_dur,
            actual_dur - target_dur,
        )

    return actual_dur


def build_sync_audio(
    segments: list[tuple[float, float, str]],
    video_duration: float,
    tmp_dir: str,
    output_path: str,
) -> None:
    """
    Adaptively synchronize translated speech.

    - Uses gaps before the next segment.
    - Speeds up speech moderately when necessary.
    - Never truncates individual fitted segments.
    - Warns about overlaps and overflow.
    """
    if not segments:
        _run([
            "ffmpeg",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=mono",
            "-t", str(video_duration),
            "-c:a", "pcm_s16le",
            output_path, "-y", "-loglevel", "error",
        ])
        return

    segments = sorted(segments, key=lambda s: s[0])
    fitted_files: list[tuple[float, str, float]] = []

    for i, (start, end, seg_audio) in enumerate(segments):
        slot = max(end - start, 0.2)

        if i + 1 < len(segments):
            next_start = segments[i + 1][0]
            available = max(next_start - start, slot)
        else:
            available = max(video_duration - start, slot)

        fit_out = os.path.join(tmp_dir, f"fit_{i}.mp3")

        actual_duration = fit_segment(
            audio_path=seg_audio,
            target_dur=available,
            output_path=fit_out,
            max_speed=1.5,
        )

        actual_end = start + actual_duration

        if i + 1 < len(segments):
            next_start = segments[i + 1][0]

            if actual_end > next_start:
                logger.warning(
                    "Segment %d overlaps next segment by %.2fs",
                    i,
                    actual_end - next_start,
                )

        if actual_end > video_duration:
            logger.warning(
                "Segment %d exceeds video duration by %.2fs",
                i,
                actual_end - video_duration,
            )

        fitted_files.append((start, fit_out, actual_duration))

    inputs: list[str] = []
    filters: list[str] = []

    for i, (start, fit_path, _) in enumerate(fitted_files):
        inputs += ["-i", fit_path]

        delay_ms = max(0, round(start * 1000))
        filters.append(
            f"[{i}:a]adelay={delay_ms}:all=1[s{i}]"
        )

    n = len(fitted_files)
    mix = "".join(f"[s{i}]" for i in range(n))

    filters.append(
        f"{mix}amix=inputs={n}:"
        "normalize=0:dropout_transition=0[out]"
    )

    # Keep all speech in the generated audio.
    output_duration = max(
        video_duration,
        max(
            start + duration
            for start, _, duration in fitted_files
        ),
    )

    _run([
        "ffmpeg",
        *inputs,
        "-filter_complex", ";".join(filters),
        "-map", "[out]",
        "-t", str(output_duration),
        "-ar", "44100",
        "-ac", "1",
        "-c:a", "libmp3lame",
        output_path,
        "-y", "-loglevel", "error",
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