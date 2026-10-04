from dataclasses import dataclass
from core.exceptions import TranscriptionError
from config import settings


@dataclass
class Segment:
    start: float
    end:   float
    text:  str


def transcribe_segments(audio_path: str, lang_code: str | None) -> list[Segment]:
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type="int8",
        )
        raw, _ = model.transcribe(audio_path, language=lang_code, word_timestamps=True)
        return [Segment(start=s.start, end=s.end, text=s.text.strip()) for s in raw]
    except Exception as e:
        raise TranscriptionError(f"Whisper: {e}") from e


def transcribe(audio_path: str, lang_code: str | None) -> str:
    return " ".join(s.text for s in transcribe_segments(audio_path, lang_code))