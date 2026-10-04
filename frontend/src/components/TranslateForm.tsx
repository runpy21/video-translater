import { useState, useEffect, FormEvent } from 'react';
import type { TranslateRequest, Backend, Languages } from '../types';

const BACKENDS: { value: Backend; label: string }[] = [
  { value: 'nllb', label: 'NLLB-200 (recommended, local)' },
  { value: 'ollama', label: 'Ollama' },
  { value: 'lm_studio', label: 'LM Studio' },
  { value: 'anthropic', label: 'Anthropic Claude (paid)' },
  { value: 'custom', label: 'Own server' },
];

interface Props {
  onSubmit: (req: TranslateRequest) => void;
}

export function TranslateForm({ onSubmit }: Props) {
  const [langs, setLangs] = useState<Languages | null>(null);
  const [url, setUrl] = useState('');
  const [srcLang, setSrcLang] = useState<string | null>(null);
  const [tgtLang, setTgtLang] = useState('');
  const [backend, setBackend] = useState<Backend>('nllb');
  const [model, setModel] = useState('qwen2.5:7b');
  const [apiKey, setApiKey] = useState('');
  const [customUrl, setCustomUrl] = useState('');

  // load languages from backend
  useEffect(() => {
    fetch('/api/languages')
      .then((r) => r.json())
      .then((data: Languages) => {
        setLangs(data);
        setSrcLang(null);
        setTgtLang(data.target[0]?.value ?? '');
        setModel(data.models[0] ?? 'qwen2.5:7b');
      });
  }, []);

  const isCloud = backend === 'anthropic';
  const isLocal = backend === 'ollama' || backend === 'lm_studio';
  const isCustom = backend === 'custom';
  const isNLLB = backend === 'nllb';

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit({
      url,
      source_lang: srcLang,
      target_lang: tgtLang,
      backend,
      api_key: apiKey,
      model,
      custom_url: customUrl,
    });
  }

  if (!langs) return <p className="loading">Loading languages...</p>;

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="field">
        <label>Link</label>
        <input
          type="url"
          required
          placeholder="https://www.instagram.com/... or https://youtube.com/..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
      </div>

      <div className="field-row">
        <div className="field">
          <label>Source language</label>
          <select value={srcLang ?? ''} onChange={(e) => setSrcLang(e.target.value || null)}>
            {langs.source.map((l) => (
              <option key={l.label} value={l.value ?? ''}>
                {l.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label>Target language</label>
          <select value={tgtLang} onChange={(e) => setTgtLang(e.target.value)}>
            {langs.target.map((l) => (
              <option key={l.label} value={l.value}>
                {l.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="field">
        <label>Backend for translation</label>
        <select value={backend} onChange={(e) => setBackend(e.target.value as Backend)}>
          {BACKENDS.map((b) => (
            <option key={b.value} value={b.value}>
              {b.label}
            </option>
          ))}
        </select>
      </div>

      {(isLocal || isCustom) && (
        <div className="field">
          <label>Model</label>
          <select value={model} onChange={(e) => setModel(e.target.value)}>
            {langs.models.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </div>
      )}

      {(isCloud || isCustom) && (
        <div className="field">
          <label>🔑 API Key</label>
          <input
            type="password"
            placeholder={isCustom ? 'optional' : 'sk-ant-api03-...'}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        </div>
      )}

      {isCustom && (
        <div className="field">
          <label>server URL</label>
          <input
            type="url"
            placeholder="http://localhost:11434/v1"
            value={customUrl}
            onChange={(e) => setCustomUrl(e.target.value)}
          />
        </div>
      )}

      <button type="submit" className="btn-primary">
        Translate video
      </button>
    </form>
  );
}
