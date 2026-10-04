import { useState, useRef, useCallback } from 'react';
import type { TranslateRequest, TranslationResult, JobEvent } from '../types';

export type Status = 'idle' | 'pending' | 'streaming' | 'done' | 'error';

export function useTranslation() {
  const [status, setStatus] = useState<Status>('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<TranslationResult | null>(null);
  const [error, setError] = useState('');
  const esRef = useRef<EventSource | null>(null);

  const translate = useCallback(async (req: TranslateRequest) => {
    esRef.current?.close();
    setStatus('pending');
    setProgress(0);
    setMessage('Request to server...');
    setResult(null);
    setError('');

    try {
      const res = await fetch('/api/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { job_id } = await res.json();

      setStatus('streaming');
      const es = new EventSource(`/api/jobs/${job_id}/stream`);
      esRef.current = es;

      es.onmessage = (e: MessageEvent) => {
        const event: JobEvent = JSON.parse(e.data);

        if (event.type === 'progress') {
          setProgress(event.pct ?? 0);
          setMessage(event.message ?? '');
        } else if (event.type === 'done') {
          setStatus('done');
          setProgress(1);
          setResult({
            videoUrl: event.video_url!,
            transcript: event.transcript!,
            translation: event.translation!,
          });
          es.close();
        } else if (event.type === 'error') {
          setStatus('error');
          setError(event.message ?? 'Unknown error');
          es.close();
        }
      };

      es.onerror = () => {
        setStatus('error');
        setError('The connection to the server has been lost');
        es.close();
      };
    } catch (err) {
      setStatus('error');
      setError(String(err));
    }
  }, []);

  const reset = useCallback(() => {
    esRef.current?.close();
    setStatus('idle');
    setProgress(0);
    setMessage('');
    setResult(null);
    setError('');
  }, []);

  return { status, progress, message, result, error, translate, reset };
}
