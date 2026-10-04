from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    output_dir: str = "outputs"
    server_port: int = 7861

    # Whisper
    whisper_model: str = "base"        # base / small / medium / large-v3
    whisper_device: str = "cpu"        # cpu / cuda

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    # Ollama
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_default_model: str = "qwen2.5:7b"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
