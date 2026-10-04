import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from core.models import TranslationJob, TranslatorBackend
from services.pipeline import TranslationPipeline
from utils.languages import TARGET_LANGUAGES
from . import jobs as job_store
from .schemas import TranslateRequest

router = APIRouter()
pipeline = TranslationPipeline()


_executor = ThreadPoolExecutor(max_workers=2)


# ── POST /api/jobs ────────────────────────────────────────────────────────────

@router.post("/jobs", status_code=202)
async def create_job(req: TranslateRequest):
    """Runs the pipeline in the background and immediately returns the job_id."""
    job  = job_store.create()
    loop = asyncio.get_event_loop()

    def on_progress(pct: float, msg: str) -> None:
        """Called from a worker thread—we safely place the event in the queue."""
        asyncio.run_coroutine_threadsafe(
            job.queue.put({"type": "progress", "pct": pct, "message": msg}),
            loop,
        )

    def run() -> None:
        try:
            translation_job = TranslationJob(
                url=req.url,
                source_lang=req.source_lang,
                target_lang=TARGET_LANGUAGES[req.target_lang]["name"],
                target_voice=TARGET_LANGUAGES[req.target_lang]["edge"],
                backend=TranslatorBackend(req.backend),
                api_key=req.api_key,
                model=req.model,
                custom_url=req.custom_url,
            )
            result = pipeline.run(translation_job, on_progress=on_progress)

            job.status      = job_store.JobStatus.DONE
            job.video_path  = result.video_path
            job.transcript  = result.transcript
            job.translation = result.translation

            asyncio.run_coroutine_threadsafe(
                job.queue.put({
                    "type":        "done",
                    "video_url":   f"/api/jobs/{job.id}/video",
                    "transcript":  result.transcript,
                    "translation": result.translation,
                }),
                loop,
            )
        except Exception as exc:
            job.status = job_store.JobStatus.ERROR
            job.error  = str(exc)
            asyncio.run_coroutine_threadsafe(
                job.queue.put({"type": "error", "message": str(exc)}),
                loop,
            )

    loop.run_in_executor(_executor, run)
    return {"job_id": job.id}


# ── GET /api/jobs/{id}/stream  (SSE) ─────────────────────────────────────────

@router.get("/jobs/{job_id}/stream")
async def stream_job(job_id: str):
    """
    Server-Sent Events — streams progress in real time.
    Events: progress | done | error | heartbeat
    """
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    async def generator():
        while True:
            try:
                event = await asyncio.wait_for(job.queue.get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event["type"] in ("done", "error"):
                    break
            except asyncio.TimeoutError:
                yield 'data: {"type":"heartbeat"}\n\n'

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",  
        },
    )


# ── GET /api/jobs/{id}/video ──────────────────────────────────────────────────

@router.get("/jobs/{job_id}/video")
async def get_video(job_id: str):
    """Returns the finished video."""
    job = job_store.get(job_id)
    if not job or not job.video_path:
        raise HTTPException(404, "Video not ready")
    return FileResponse(
        job.video_path,
        media_type="video/mp4",
        filename="translated.mp4",
    )


# ── GET /api/languages ────────────────────────────────────────────────────────

@router.get("/languages")
async def get_languages():
    """Returns lists of languages for front-end drop-down menus."""
    from utils.languages import SOURCE_LANGUAGES, TARGET_LANGUAGES, OLLAMA_MODELS
    return {
        "source": [
            {"label": k, "value": v} for k, v in SOURCE_LANGUAGES.items()
        ],
        "target": [
            {"label": k, "value": k} for k in TARGET_LANGUAGES
        ],
        "models": OLLAMA_MODELS,
    }
