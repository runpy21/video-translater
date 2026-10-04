import shutil
import time
from pathlib import Path

from core.ports import BaseStorage
from config import settings


class LocalStorage(BaseStorage):
    """Stores finished videos in the local outputs/ folder."""
    def __init__(self) -> None:
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save(self, source_path: str) -> str:
        filename = f"translated_{int(time.time())}.mp4"
        dest = self.output_dir / filename
        shutil.copy(source_path, dest)
        return str(dest)


