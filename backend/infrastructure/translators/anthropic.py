from core.ports import BaseTranslator
from core.models import TranslationJob
from core.exceptions import TranslationError
from config import settings


class AnthropicTranslator(BaseTranslator):

    def translate(self, text: str, target_lang_name: str, job: TranslationJob) -> str:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=job.api_key or settings.anthropic_api_key)
            msg = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": self._prompt(text, target_lang_name)}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            raise TranslationError(f"Anthropic: {e}") from e
