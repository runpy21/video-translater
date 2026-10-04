"""
In-memory task store.
For production, replace with Redis + Celery.
"""
import asyncio
import uuid
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE    = "done"
    ERROR   = "error"


@dataclass
class Job:
    id:          str
    status:      JobStatus         = JobStatus.PENDING
    video_path:  str | None        = None
    transcript:  str | None        = None
    translation: str | None        = None
    error:       str | None        = None
    # Кожен SSE-event кладемо в цю чергу
    queue:       asyncio.Queue     = field(default_factory=asyncio.Queue)


_store: dict[str, Job] = {}


def create() -> Job:
    job = Job(id=str(uuid.uuid4()))
    _store[job.id] = job
    return job


def get(job_id: str) -> Job | None:
    return _store.get(job_id)
