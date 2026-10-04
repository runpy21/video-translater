export type Backend = 'ollama' | 'lm_studio' | 'anthropic' | 'custom' | 'nllb';

export interface TranslateRequest {
  url: string;
  source_lang: string | null;
  target_lang: string;
  backend: Backend;
  api_key?: string;
  model?: string;
  custom_url?: string;
}

export type JobEventType = 'progress' | 'done' | 'error' | 'heartbeat';

export interface JobEvent {
  type: JobEventType;
  pct?: number;
  message?: string;
  video_url?: string;
  transcript?: string;
  translation?: string;
}

export interface Languages {
  source: { label: string; value: string | null }[];
  target: { label: string; value: string }[];
  models: string[];
}

export interface TranslationResult {
  videoUrl: string;
  transcript: string;
  translation: string;
}
