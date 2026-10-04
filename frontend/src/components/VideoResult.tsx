import type { TranslationResult } from '../types';

interface Props {
  result: TranslationResult;
  onReset: () => void;
}

export function VideoResult({ result, onReset }: Props) {
  return (
    <div className="result">
      <div className="result-header">
        <h2>Done!</h2>
        <button className="btn-secondary" onClick={onReset}>
          New video
        </button>
      </div>

      <video className="video-player" src={result.videoUrl} controls autoPlay />

      <a className="btn-primary download" href={result.videoUrl} download="translated.mp4">
        Download video
      </a>

      <div className="transcripts">
        <div className="transcript-box">
          <h3>Original</h3>
          <p>{result.transcript}</p>
        </div>
        <div className="transcript-box">
          <h3>Translation</h3>
          <p>{result.translation}</p>
        </div>
      </div>
    </div>
  );
}
