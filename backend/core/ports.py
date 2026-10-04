from abc import ABC, abstractmethod
from .models import TranslationJob


class BaseTranslator(ABC):
    """A contract for any translator.
    Add a new backend = implement this class."""

    @abstractmethod
    def translate(self, text: str, target_lang_name: str, job: TranslationJob) -> str: ...

    def _prompt(self, text: str, lang: str) -> str:
        return (
            f"Translate the following text to {lang}. "
            "Keep the same natural conversational tone and style. "
            "Return ONLY the translation, no explanations:\n\n"
            f"{text}"
        )


class BaseStorage(ABC):
    """A contract for storing results."""

    @abstractmethod
    def save(self, source_path: str) -> str: ...
