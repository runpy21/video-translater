from dataclasses import dataclass, field
from enum import Enum


class TranslatorBackend(str, Enum):
    ANTHROPIC  = "anthropic"
    OLLAMA     = "ollama"
    LM_STUDIO  = "lm_studio"
    CUSTOM     = "custom"
    NLLB       = "nllb"


@dataclass
class TranslationJob:
    """Description of a video translation assignment."""
    url:          str
    source_lang:  str | None          # None → Whisper визначить автоматично
    target_lang:  str                 # "Ukrainian", "Polish" …
    target_voice: str                 # Edge TTS voice id
    backend:      TranslatorBackend
    api_key:      str = ""
    model:        str = "qwen2.5:7b"
    custom_url:   str = ""


@dataclass
class PipelineResult:
    """The result of the pipeline running successfully."""
    video_path:  str
    transcript:  str
    translation: str
