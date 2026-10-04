import os
import sys  # ← додай
import subprocess
from pathlib import Path
from core.exceptions import VideoProcessingError


def separate(audio_path: str, output_dir: str) -> tuple[str, str]:
    try:
        subprocess.run(
            [
                sys.executable,  # ← замість "python"
                "-m", "demucs",
                "--two-stems", "vocals",
                "--out", output_dir,
                audio_path,
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise VideoProcessingError(f"Demucs: {e.stderr.decode(errors='ignore')}") from e

    stem       = Path(audio_path).stem
    vocals     = os.path.join(output_dir, "htdemucs", stem, "vocals.wav")
    background = os.path.join(output_dir, "htdemucs", stem, "no_vocals.wav")

    if not os.path.exists(vocals):
        raise VideoProcessingError("Demucs did not create the files—check the installation")

    return vocals, background