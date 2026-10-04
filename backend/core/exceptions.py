class VideoTranslatorError(Exception):
    """Base class—let's implement it in the UI."""


class DownloadError(VideoTranslatorError):
    """The video could not be loaded."""


class TranscriptionError(VideoTranslatorError):
    """Whisper error."""


class TranslationError(VideoTranslatorError):
    """Translation error (Anthropic / Ollama)."""


class SynthesisError(VideoTranslatorError):
    """Edge TTS error."""


class VideoProcessingError(VideoTranslatorError):
    """ffmpeg error."""
