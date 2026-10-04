from pydantic import BaseModel


class TranslateRequest(BaseModel):
    url:         str
    source_lang: str | None  # None = auto-detect
    target_lang: str         # key from TARGET_LANGUAGES
    backend:     str         # "ollama" | "lm_studio" | "anthropic" | "custom"
    api_key:     str = ""
    model:       str = "qwen2.5:7b"
    custom_url:  str = ""
