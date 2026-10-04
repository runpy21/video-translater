from core.models import TranslatorBackend
from core.ports import BaseTranslator
from config import settings
from .anthropic import AnthropicTranslator
from .ollama import OllamaTranslator
from .nllb import NLLBTranslator


def get_translator(backend: TranslatorBackend, custom_url: str = "") -> BaseTranslator:
    """
    Фабрика перекладачів.
    Щоб додати новий backend — реалізуй BaseTranslator і додай case сюди.
    """
    match backend:
        case TranslatorBackend.ANTHROPIC:
            return AnthropicTranslator()
        case TranslatorBackend.OLLAMA:
            return OllamaTranslator(settings.ollama_base_url)
        case TranslatorBackend.LM_STUDIO:
            return OllamaTranslator("http://localhost:1234/v1")
        case TranslatorBackend.CUSTOM:
            if not custom_url:
                raise ValueError("custom_url не вказано")
            return OllamaTranslator(custom_url)
        case TranslatorBackend.NLLB:
            return NLLBTranslator()
        case _:
            raise ValueError(f"Невідомий backend: {backend}")
