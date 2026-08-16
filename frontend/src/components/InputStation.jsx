import React, { useState } from 'react';
import { HardDrive, UploadCloud, Globe, Play, Sparkles, FileVideo, Tv, Film } from 'lucide-react';

export default function InputStation({ onProcess, isProcessing }) {
  const [mode, setMode] = useState('youtube'); // 'youtube' | 'local' | 'upload'
  const [youtubeUrl, setYoutubeUrl] = useState('https://youtu.be/YBJEiWDPyGs?si=LBU4kBgvfURBVF-b');
  const [localPath, setLocalPath] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [language, setLanguage] = useState('english');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (mode === 'youtube') {
      if (!youtubeUrl.trim()) return;
      onProcess({ type: 'url', source: youtubeUrl.trim(), language });
    } else if (mode === 'local') {
      if (!localPath.trim()) return;
      onProcess({ type: 'url', source: localPath.trim(), language });
    } else if (mode === 'upload') {
      if (!selectedFile) return;
      onProcess({ type: 'file', file: selectedFile, language });
    }
  };

  return (
    <div className="glass-card-3d" style={{
      maxWidth: '900px',
      margin: '40px auto',
      padding: '36px',
      borderRadius: '24px',
      border: '1px solid rgba(0, 240, 255, 0.25)',
      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.7), 0 0 35px rgba(0, 240, 255, 0.15)',
    }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '28px' }}>
        <div className="badge-neon badge-cyan" style={{ marginBottom: '12px' }}>
          <Sparkles size={13} /> NEURAL VIDEO INGESTION
        </div>
        <h2 className="font-display" style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px' }}>
          Drop in any video, <span className="text-gradient-cyan">unlock instant intelligence.</span>
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
          Speech-to-text with Whisper, automated summaries, key decision extraction, and instant reel generator.
        </p>
      </div>

      {/* Mode Selector Tabs */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
        padding: '6px',
        background: 'rgba(3, 7, 18, 0.6)',
        borderRadius: '16px',
        marginBottom: '28px',
        border: '1px solid rgba(255, 255, 255, 0.05)',
      }}>
        <button
          type="button"
          onClick={() => setMode('youtube')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '12px 16px',
            borderRadius: '12px',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            background: mode === 'youtube' ? 'linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(112, 0, 255, 0.3))' : 'transparent',
            color: mode === 'youtube' ? '#00f0ff' : 'var(--text-secondary)',
            border: mode === 'youtube' ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid transparent',
            boxShadow: mode === 'youtube' ? '0 0 20px rgba(0, 240, 255, 0.2)' : 'none',
          }}
        >
          <Tv size={18} /> YouTube URL
        </button>

        <button
          type="button"
          onClick={() => setMode('upload')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '12px 16px',
            borderRadius: '12px',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            background: mode === 'upload' ? 'linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(112, 0, 255, 0.3))' : 'transparent',
            color: mode === 'upload' ? '#00f0ff' : 'var(--text-secondary)',
            border: mode === 'upload' ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid transparent',
            boxShadow: mode === 'upload' ? '0 0 20px rgba(0, 240, 255, 0.2)' : 'none',
          }}
        >
          <UploadCloud size={18} /> Upload Video
        </button>

        <button
          type="button"
          onClick={() => setMode('local')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '12px 16px',
            borderRadius: '12px',
            border: 'none',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.25s ease',
            background: mode === 'local' ? 'linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(112, 0, 255, 0.3))' : 'transparent',
            color: mode === 'local' ? '#00f0ff' : 'var(--text-secondary)',
            border: mode === 'local' ? '1px solid rgba(0, 240, 255, 0.4)' : '1px solid transparent',
            boxShadow: mode === 'local' ? '0 0 20px rgba(0, 240, 255, 0.2)' : 'none',
          }}
        >
          <HardDrive size={18} /> Local File Path
        </button>
      </div>

      {/* Form Area */}
      <form onSubmit={handleSubmit}>
        {mode === 'youtube' && (
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>
              YOUTUBE VIDEO LINK
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="url"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://youtu.be/..."
                required
                style={{
                  width: '100%',
                  padding: '16px 20px',
                  background: 'rgba(3, 7, 18, 0.8)',
                  border: '1px solid rgba(0, 240, 255, 0.3)',
                  borderRadius: '14px',
                  color: '#fff',
                  fontSize: '1rem',
                  outline: 'none',
                  fontFamily: 'var(--font-mono)',
                  boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)',
                }}
              />
            </div>
          </div>
        )}

        {mode === 'local' && (
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>
              LOCAL VIDEO / AUDIO ABSOLUTE PATH
            </label>
            <input
              type="text"
              value={localPath}
              onChange={(e) => setLocalPath(e.target.value)}
              placeholder="e.g. D:\Videos\keynote.mp4 or downloads/YBJEiWDPyGs.mp4"
              required
              style={{
                width: '100%',
                padding: '16px 20px',
                background: 'rgba(3, 7, 18, 0.8)',
                border: '1px solid rgba(0, 240, 255, 0.3)',
                borderRadius: '14px',
                color: '#fff',
                fontSize: '1rem',
                outline: 'none',
                fontFamily: 'var(--font-mono)',
              }}
            />
          </div>
        )}

        {mode === 'upload' && (
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>
              DRAG & DROP OR SELECT MEDIA FILE
            </label>
            <div
              style={{
                border: '2px dashed rgba(0, 240, 255, 0.35)',
                borderRadius: '16px',
                padding: '36px 20px',
                textAlign: 'center',
                background: 'rgba(3, 7, 18, 0.5)',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
              }}
              onClick={() => document.getElementById('file-input').click()}
            >
              <input
                id="file-input"
                type="file"
                accept="video/*,audio/*"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setSelectedFile(e.target.files[0]);
                  }
                }}
              />
              <FileVideo size={40} color="#00f0ff" style={{ margin: '0 auto 12px', opacity: 0.8 }} />
              {selectedFile ? (
                <div>
                  <p style={{ fontWeight: 700, color: 'var(--cyan-neon)' }}>{selectedFile.name}</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div>
                  <p style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Click to browse or drop your MP4, MKV, MP3 file here</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>Supports all standard video and audio formats</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Controls Row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Globe size={18} color="var(--cyan-neon)" />
            <label style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Audio Engine:</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              style={{
                padding: '8px 14px',
                background: 'rgba(11, 17, 34, 0.9)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '0.9rem',
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              <option value="english">Whisper Small (English / Global)</option>
              <option value="hinglish">AI4Bharat IndicWhisper (Hinglish)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={isProcessing}
            className="btn-cyber-primary"
            style={{ minWidth: '220px', justifyContent: 'center' }}
          >
            <Play size={18} fill="#030712" />
            {isProcessing ? 'Processing Matrix...' : 'Generate Video Intelligence'}
          </button>
        </div>
      </form>
    </div>
  );
}
