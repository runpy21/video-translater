import { useTranslation } from './hooks/useTranslation';
import { TranslateForm } from './components/TranslateForm';
import { ProgressTracker } from './components/ProgressTracker';
import { VideoResult } from './components/VideoResult';

export default function App() {
  const { status, progress, message, result, error, translate, reset } = useTranslation();

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Translate video</h1>
          <p>supported platforms youtube.com, youtu.be, vimeo.com, tiktok.com, instagram.com</p>
        </div>
      </header>

      <main className="main">
        {status === 'idle' && <TranslateForm onSubmit={translate} />}

        {(status === 'pending' || status === 'streaming') && (
          <ProgressTracker progress={progress} message={message} />
        )}

        {status === 'done' && result && <VideoResult result={result} onReset={reset} />}

        {status === 'error' && (
          <div className="error-box">
            <h2>Error</h2>
            <pre>{error}</pre>
            <button className="btn-primary" onClick={reset}>
              Try again
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
