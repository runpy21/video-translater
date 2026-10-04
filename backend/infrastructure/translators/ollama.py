from core.ports import BaseTranslator
from core.models import TranslationJob
from core.exceptions import TranslationError


class OllamaTranslator(BaseTranslator):

    def __init__(self, base_url: str):
        self.base_url = base_url

    def translate(self, text: str, target_lang_name: str, job: TranslationJob) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=self.base_url, api_key="ollama")
            resp = client.chat.completions.create(
                model=job.model,
                messages=[{"role": "user", "content": self._prompt(text, target_lang_name)}],
                max_tokens=2048,
            )
            content = resp.choices[0].message.content
            if not content:
                finish = resp.choices[0].finish_reason
                raise TranslationError(
                    f"Ollama повернула порожню відповідь (finish_reason={finish}). "
                    "Спробуй ще раз або перезапусти Ollama."
                )
            return content.strip()
        except TranslationError:
            raise
        except Exception as e:
            raise TranslationError(f"Ollama ({self.base_url}): {e}") from e
