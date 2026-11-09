import { useState } from 'react';
import './ShortsStudio.css';

export default function ShortsStudio() {
  const [url, setUrl] = useState('');
  const [running, setRunning] = useState(false);
  const [batch, setBatch] = useState(null);
  const [error, setError] = useState('');
  const [copyStatus, setCopyStatus] = useState('');

  async function generate(event) {
    event.preventDefault();
    setRunning(true);
    setError('');
    setCopyStatus('');
    try {
      const response = await fetch('/api/shorts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Could not create shorts.');
      setBatch(data);
    } catch (failure) {
      setError(failure instanceof SyntaxError
        ? 'Relent returned an unreadable response. Check the local backend terminal.'
        : failure.message);
    } finally {
      setRunning(false);
    }
  }

  async function copyMetadata(clip, index) {
    try {
      await navigator.clipboard.writeText(
        [clip.title, clip.description, clip.hashtags.join(' ')].join('\n\n'),
      );
      setCopyStatus(`Copied metadata for Short ${index + 1}.`);
    } catch {
      setCopyStatus('Clipboard is unavailable. You can still download the metadata file.');
    }
  }

  return (
    <main className="shorts-studio">
      <header className="shorts-heading">
        <a href="/">Relent AI</a>
        <h1>Shorts Studio</h1>
        <p>Turn one YouTube video into up to ten captioned vertical clips.</p>
      </header>

      <form className="shorts-form glass-card-3d" onSubmit={generate}>
        <label htmlFor="shorts-source">YouTube video link</label>
        <input
          id="shorts-source"
          type="url"
          placeholder="https://www.youtube.com/watch?v=…"
          required
          disabled={running}
          value={url}
          onChange={(event) => setUrl(event.target.value)}
        />
        <button className="btn-cyber-primary" disabled={running}>
          {running ? 'Creating shorts…' : 'Generate shorts'}
        </button>
        <p>Use a finished video up to 30 minutes long. Groq processes the audio and transcript. FFmpeg renders the clips on this computer.</p>
      </form>

      {running && <p role="status">Downloading, transcribing, selecting, and rendering. Keep this tab open while Relent works.</p>}
      {error && <p className="shorts-error" role="alert">{error}</p>}

      {batch && (
        <section aria-labelledby="shorts-results">
          <div className="shorts-results-heading">
            <h2 id="shorts-results">{batch.clips.length} {batch.clips.length === 1 ? 'short' : 'shorts'} ready</h2>
            <a href={batch.metadata_url} download>Download all metadata</a>
          </div>
          {batch.clips.length < batch.requested_count && (
            <p>Relent found {batch.clips.length} distinct spoken moments long enough to use.</p>
          )}
          <p className="shorts-copy-status" role="status">{copyStatus}</p>
          <div className="shorts-grid">
            {batch.clips.map((clip, index) => (
              <article key={clip.video_url} className="shorts-card glass-card-3d">
                <video controls playsInline preload="none" src={clip.video_url} aria-label={clip.title} />
                <p className="shorts-range">Short {index + 1} · {clip.source_start.toFixed(1)}–{clip.source_end.toFixed(1)}s in source</p>
                <h3>{clip.title}</h3>
                <p>{clip.description}</p>
                <p className="shorts-tags">{clip.hashtags.join(' ')}</p>
                <div className="shorts-actions">
                  <a href={`${clip.video_url}?download=1`} download>Download MP4</a>
                  <button type="button" onClick={() => copyMetadata(clip, index)}>Copy metadata</button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
