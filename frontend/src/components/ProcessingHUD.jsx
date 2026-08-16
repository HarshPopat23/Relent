import React, { useEffect, useState } from 'react';
import { Cpu, Database, Disc, FileAudio, Layers, Sparkles } from 'lucide-react';

const STAGES = [
  { id: 1, label: 'Demuxing Video Stream & Normalizing Audio Chunks', icon: FileAudio },
  { id: 2, label: 'Running Whisper Multi-Chunk Timestamp Transcription', icon: Disc },
  { id: 3, label: 'Building Chroma Vector Space & Knowledge Embeddings', icon: Database },
  { id: 4, label: 'Ollama Neural Synthesis: Map-Reduce Summary & Insights', icon: Cpu },
];

export default function ProcessingHUD() {
  const [currentStage, setCurrentStage] = useState(1);

  useEffect(() => {
    const timer1 = setTimeout(() => setCurrentStage(2), 4000);
    const timer2 = setTimeout(() => setCurrentStage(3), 15000);
    const timer3 = setTimeout(() => setCurrentStage(4), 28000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(3, 7, 18, 0.88)',
      backdropFilter: 'blur(24px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '24px',
    }}>
      <div className="glass-card-3d" style={{
        maxWidth: '600px',
        width: '100%',
        padding: '40px',
        textAlign: 'center',
        border: '1px solid rgba(0, 240, 255, 0.4)',
        boxShadow: '0 0 80px rgba(0, 240, 255, 0.25)',
      }}>
        {/* Hologram Rings */}
        <div style={{
          position: 'relative',
          width: '120px',
          height: '120px',
          margin: '0 auto 28px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <div style={{
            position: 'absolute',
            inset: 0,
            borderRadius: '50%',
            border: '2px dashed rgba(0, 240, 255, 0.6)',
            animation: 'spin 10s linear infinite',
          }} />
          <div style={{
            position: 'absolute',
            inset: '12px',
            borderRadius: '50%',
            border: '2px solid rgba(157, 78, 221, 0.5)',
            borderTopColor: 'transparent',
            animation: 'spin 4s linear infinite reverse',
          }} />
          <Sparkles size={40} color="#00f0ff" className="anim-pulse-glow" />
        </div>

        <h3 className="font-display" style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '8px' }}>
          NEURAL PIPELINE <span className="text-gradient-cyan">ACTIVE</span>
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '24px' }}>
          Extracting knowledge matrix, time-aligned transcript, and LLM reasoning.
        </p>

        {/* Audio Visualizer Wave */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
          height: '48px',
          marginBottom: '32px',
        }}>
          {[...Array(12)].map((_, i) => (
            <div key={i} className="wave-bar" style={{ animationDelay: `${(i * 0.1).toFixed(2)}s` }} />
          ))}
        </div>

        {/* Live Stages */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', textAlign: 'left' }}>
          {STAGES.map((stg) => {
            const Icon = stg.icon;
            const isDone = currentStage > stg.id;
            const isCurrent = currentStage === stg.id;

            return (
              <div
                key={stg.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: '12px',
                  background: isCurrent
                    ? 'rgba(0, 240, 255, 0.12)'
                    : isDone
                    ? 'rgba(0, 255, 157, 0.06)'
                    : 'rgba(255, 255, 255, 0.02)',
                  border: isCurrent
                    ? '1px solid rgba(0, 240, 255, 0.4)'
                    : isDone
                    ? '1px solid rgba(0, 255, 157, 0.2)'
                    : '1px solid rgba(255, 255, 255, 0.04)',
                  transition: 'all 0.3s ease',
                }}
              >
                <div style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: isCurrent ? 'var(--cyan-neon)' : isDone ? 'var(--emerald-neon)' : 'rgba(255, 255, 255, 0.1)',
                  color: isCurrent || isDone ? '#030712' : '#fff',
                }}>
                  <Icon size={16} />
                </div>
                <span style={{
                  fontSize: '0.85rem',
                  fontWeight: isCurrent ? 700 : 500,
                  color: isCurrent ? '#00f0ff' : isDone ? '#00ff9d' : 'var(--text-muted)',
                }}>
                  {stg.label}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
