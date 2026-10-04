from __future__ import annotations
from typing import ClassVar, Any
from core.ports import BaseTranslator
from core.models import TranslationJob
from core.exceptions import TranslationError

# Не крашимо сервер якщо transformers не встановлений
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

NLLB_TARGET: dict[str, str] = {
    "Ukrainian": "ukr_Cyrl", "Polish":     "pol_Latn",
    "German":    "deu_Latn", "French":     "fra_Latn",
    "Spanish":   "spa_Latn", "Italian":    "ita_Latn",
    "Portuguese":"por_Latn", "Romanian":   "ron_Latn",
    "Czech":     "ces_Latn", "Hungarian":  "hun_Latn",
    "English":   "eng_Latn",
}
NLLB_SOURCE: dict[str, str] = {
    "en": "eng_Latn", "uk": "ukr_Cyrl", "de": "deu_Latn",
    "fr": "fra_Latn", "es": "spa_Latn", "it": "ita_Latn",
    "pt": "por_Latn", "ja": "jpn_Jpan", "ko": "kor_Hang",
    "zh": "zho_Hans", "ru": "rus_Cyrl",
}


class NLLBTranslator(BaseTranslator):
    MODEL_ID = "facebook/nllb-200-distilled-1.3B"
    _tokenizer: ClassVar[Any] = None
    _model:     ClassVar[Any] = None

    def _load(self) -> None:
        if not TRANSFORMERS_AVAILABLE:
            raise TranslationError(
                "transformers не встановлений. Запусти: "
                "pip install transformers sentencepiece torch"
            )
        if NLLBTranslator._model is not None:
            return
        NLLBTranslator._tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID)
        NLLBTranslator._model     = AutoModelForSeq2SeqLM.from_pretrained(self.MODEL_ID)

    def translate(self, text: str, target_lang_name: str, job: TranslationJob) -> str:
        try:
            self._load()
            src = NLLB_SOURCE.get(job.source_lang or "en", "eng_Latn")
            tgt = NLLB_TARGET.get(target_lang_name)
            if not tgt:
                raise TranslationError(f"NLLB: невідома мова '{target_lang_name}'")

            tok: Any = NLLBTranslator._tokenizer
            mdl: Any = NLLBTranslator._model
            tok.src_lang = src
            inputs  = tok(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = mdl.generate(
                **inputs,
                forced_bos_token_id=tok.convert_tokens_to_ids(tgt),
                max_length=512,
            )
            return tok.batch_decode(outputs, skip_special_tokens=True)[0]
        except TranslationError:
            raise
        except Exception as e:
            raise TranslationError(f"NLLB: {e}") from e