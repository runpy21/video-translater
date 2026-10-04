import os
from pathlib import Path

from core.exceptions import DownloadError


def download(url: str, work_dir: str) -> str:
    """Downloads a video from the URL, returns path to the file."""
    try:
        import yt_dlp

        output_template = os.path.join(work_dir, "original.%(ext)s")
        ydl_opts = {
            "outtmpl": output_template,
            "format": (
                "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/"
                "best[ext=mp4][height<=720]/best[ext=mp4]/best"
            ),
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        for f in Path(work_dir).glob("original.*"):
            return str(f)

        raise DownloadError("File not found after download")

    except DownloadError:
        raise
    except Exception as e:
        raise DownloadError(f"Failed to download video: {e}") from e
