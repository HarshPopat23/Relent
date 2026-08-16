import React from 'react';
import { Cpu, Radio, Sparkles, Video } from 'lucide-react';

export default function Navbar({ backendStatus }) {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '20px 36px',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      background: 'rgba(6, 8, 16, 0.85)',
      backdropFilter: 'blur(20px)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          width: '46px',
          height: '46px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #00f0ff 0%, #7000ff 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(0, 240, 255, 0.5)',
        }}>
          <Video size={24} color="#030712" strokeWidth={2.5} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 className="font-display" style={{
              fontSize: '1.4rem',
              fontWeight: 800,
              letterSpacing: '-0.5px',
              color: '#fff',
            }}>
              Relent AI<span className="text-gradient-cyan"></span>
            </h1>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Neural Video Intelligence, RAG Knowledge Graph & AI Reel Clipper
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div className="badge-neon badge-purple" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Cpu size={14} />
          <span>LLM: {backendStatus?.model || 'qwen2.5:3b-instruct'}</span>
        </div>

        <div className="badge-neon badge-emerald" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Radio size={14} className="anim-pulse-glow" />
          <span>Ollama: {backendStatus?.status === 'online' ? 'Active' : 'Offline'}</span>
        </div>
      </div>
    </header>
  );
}
