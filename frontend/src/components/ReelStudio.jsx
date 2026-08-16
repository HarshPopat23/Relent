import React, { useState } from 'react';
import { Clapperboard, Download, Film, Play, Scissors, Sparkles } from 'lucide-react';

export default function ReelStudio({ onGenerateReel, isGeneratingReel, reelResult }) {
  const [reelPrompt, setReelPrompt] = useState('');

  const samplePrompts = [
    '1 minute script on RTX 50 Blackwell specs and architecture',
    '30 seconds on DLSS neural rendering and energy efficiency',
    '45 seconds on GPU pricing, laptops and availability',
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!reelPrompt.trim()) return;
    onGenerateReel(reelPrompt.trim());
  };

  return (
    <div className="glass-card-3d" style={{
      padding: '32px',
      border: '1px solid rgba(157, 78, 221, 0.35)',
      boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(157, 78, 221, 0.15)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #9d4edd 0%, #ff007f 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Film size={20} color="#fff" />
        </div>
        <div>
          <h3 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 800 }}>
            AI Reel & Short-Form Video Studio
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            LLM selects exact verbatim sentences in original sequence, then cuts and merges matching video timestamps.
          </p>
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ marginTop: '20px' }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input
            type="text"
            value={reelPrompt}
            onChange={(e) => setReelPrompt(e.target.value)}
            placeholder="e.g. I want a script regarding GPU pricing of 1 minute"
            required
            style={{
              flex: 1,
              padding: '14px 18px',
              background: 'rgba(3, 7, 18, 0.8)',
              border: '1px solid rgba(157, 78, 221, 0.35)',
              borderRadius: '12px',
              color: '#fff',
              fontSize: '0.95rem',
              outline: 'none',
              fontFamily: 'var(--font-mono)',
            }}
          />
          <button
            type="submit"
            disabled={isGeneratingReel}
            className="btn-cyber-primary"
            style={{
              background: 'linear-gradient(135deg, #9d4edd 0%, #ff007f 100%)',
              boxShadow: '0 0 20px rgba(157, 78, 221, 0.4)',
              minWidth: '180px',
              justifyContent: 'center',
            }}
          >
            <Scissors size={18} />
            {isGeneratingReel ? 'Cutting Reel...' : 'Generate Reel'}
          </button>
        </div>

        {/* Suggestion tags */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>PRESETS:</span>
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setReelPrompt(p)}
              style={{
                fontSize: '0.75rem',
                padding: '4px 10px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              {p}
            </button>
          ))}
        </div>
      </form>

      {/* Reel Result Area */}
      {reelResult && (
        <div style={{ marginTop: '28px', paddingTop: '24px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
          {reelResult.error ? (
            <div style={{
              padding: '16px',
              borderRadius: '12px',
              background: 'rgba(255, 51, 102, 0.1)',
              border: '1px solid rgba(255, 51, 102, 0.3)',
              color: 'var(--rose-neon)',
              fontSize: '0.9rem',
            }}>
              {reelResult.error}
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: reelResult.reel_url ? '1fr 1fr' : '1fr', gap: '24px' }}>
              {/* Script */}
              <div>
                <h4 className="font-display" style={{ fontSize: '1.1rem', color: 'var(--purple-neon)', marginBottom: '10px' }}>
                  Generated Script (Verbatim in Video Order)
                </h4>
                <div style={{
                  padding: '16px',
                  borderRadius: '12px',
                  background: 'rgba(3, 7, 18, 0.6)',
                  border: '1px solid rgba(157, 78, 221, 0.2)',
                  fontSize: '0.9rem',
                  lineHeight: 1.7,
                  color: 'var(--text-primary)',
                  maxHeight: '260px',
                  overflowY: 'auto',
                }}>
                  {reelResult.script}
                </div>
              </div>

              {/* Video & Download */}
              {reelResult.reel_url && (
                <div>
                  <h4 className="font-display" style={{ fontSize: '1.1rem', color: 'var(--cyan-neon)', marginBottom: '10px' }}>
                    Rendered Reel Video
                  </h4>
                  <div style={{
                    borderRadius: '12px',
                    overflow: 'hidden',
                    background: '#000',
                    border: '1px solid rgba(0, 240, 255, 0.3)',
                    marginBottom: '12px',
                  }}>
                    <video src={reelResult.reel_url} controls style={{ width: '100%', maxHeight: '240px', display: 'block' }} />
                  </div>
                  <a
                    href={reelResult.reel_url}
                    download="nexus_reel.mp4"
                    className="btn-cyber-primary"
                    style={{ width: '100%', justifyContent: 'center', textDecoration: 'none' }}
                  >
                    <Download size={18} /> Download Reel MP4
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
