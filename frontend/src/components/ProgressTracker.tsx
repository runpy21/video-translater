interface Props {
  progress: number;
  message: string;
}

export function ProgressTracker({ progress, message }: Props) {
  const pct = Math.round(progress * 100);

  return (
    <div className="progress-wrap">
      <div className="progress-label">
        <span>{message || 'Processing...'}</span>
        <span className="progress-pct">{pct}%</span>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <p className="progress-hint">Please do not close the tab!</p>
    </div>
  );
}
