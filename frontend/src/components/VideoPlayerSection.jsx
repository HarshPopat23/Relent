import React, { useState } from 'react';
import { Copy, FileText, Search, Video, Volume2 } from 'lucide-react';

export default function VideoPlayerSection({ videoUrl, transcript }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [copied, setCopied] = useState(false);

  const handleCopyTranscript = () => {
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredTranscript = transcript
    ? transcript
        .split('. ')
        .filter((sentence) => sentence.toLowerCase().includes(searchTerm.toLowerCase()))
        .join('. ')
    : '';

  return (
    <div style={{ display: 'grid', gridTemplateColumns: videoUrl ? '1fr 1fr' : '1fr', gap: '24px' }}>
      {/* Video Player */}
      {videoUrl && (
        <div className="glass-card-3d" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Video size={20} color="var(--cyan-neon)" />
            <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              Synchronized Video Source
            </h3>
          </div>
          <div style={{
            position: 'relative',
            borderRadius: '14px',
            overflow: 'hidden',
            background: '#000',
            border: '1px solid rgba(0, 240, 255, 0.3)',
            boxShadow: '0 10px 30px rgba(0, 0, 0, 0.8)',
          }}>
            <video
              src={videoUrl}
              controls
              style={{ width: '100%', maxHeight: '420px', display: 'block' }}
            />
          </div>
        </div>
      )}

      {/* Interactive Transcript */}
      <div className="glass-card-3d" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} color="var(--purple-neon)" />
            <h3 className="font-display" style={{ fontSize: '1.2rem', fontWeight: 700 }}>
              Full Timestamped Transcript
            </h3>
          </div>

          <button
            onClick={handleCopyTranscript}
            className="btn-cyber-secondary"
            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
          >
            <Copy size={14} /> {copied ? 'Copied' : 'Copy All'}
          </button>
        </div>

        {/* Search filter */}
        <div style={{ position: 'relative', marginBottom: '16px' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '12px' }} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search transcript keywords..."
            style={{
              width: '100%',
              padding: '10px 14px 10px 36px',
              background: 'rgba(3, 7, 18, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '10px',
              color: '#fff',
              fontSize: '0.85rem',
              outline: 'none',
              fontFamily: 'var(--font-mono)',
            }}
          />
        </div>

        {/* Transcript Box */}
        <div style={{
          flex: 1,
          maxHeight: '340px',
          overflowY: 'auto',
          padding: '16px',
          background: 'rgba(3, 7, 18, 0.5)',
          borderRadius: '12px',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          fontSize: '0.9rem',
          lineHeight: 1.8,
          color: 'var(--text-secondary)',
          whiteSpace: 'pre-wrap',
        }}>
          {filteredTranscript || 'No matching transcript lines found.'}
        </div>
      </div>
    </div>
  );
}
