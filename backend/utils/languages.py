TARGET_LANGUAGES: dict[str, dict[str, str]] = {
    "Ukrainian":  {"edge": "uk-UA-OstapNeural",   "name": "Ukrainian"},
    "Polish":     {"edge": "pl-PL-MarekNeural",   "name": "Polish"},
    "German":     {"edge": "de-DE-ConradNeural",  "name": "German"},
    "French":     {"edge": "fr-FR-HenriNeural",   "name": "French"},
    "Spanish":    {"edge": "es-ES-AlvaroNeural",  "name": "Spanish"},
    "Italian":    {"edge": "it-IT-DiegoNeural",   "name": "Italian"},
    "Portuguese": {"edge": "pt-BR-AntonioNeural", "name": "Portuguese"},
    "Romanian":   {"edge": "ro-RO-EmilNeural",    "name": "Romanian"},
    "Czech":      {"edge": "cs-CZ-AntoninNeural", "name": "Czech"},
    "Hungarian":  {"edge": "hu-HU-TamasNeural",   "name": "Hungarian"},
    "English":    {"edge": "en-GB-RyanNeural",    "name": "English"},
}


SOURCE_LANGUAGES: dict[str, str | None] = {
    "Auto detect": None,
    "English":     "en",
    "Ukrainian":   "uk",
    "German":      "de",
    "French":      "fr",
    "Spanish":     "es",
    "Japanese":    "ja",
    "Korean":      "ko",
    "Chinese":     "zh",
    "Russian":     "ru",
}

OLLAMA_MODELS: list[str] = [
    "qwen2.5:7b",    
    "llama3.1:8b",
    "mistral:7b",
    "aya:8b",
    "llama3.2:3b",  
    "gemma2:9b",
]

