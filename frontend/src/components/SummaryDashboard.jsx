import React, { useState } from 'react';
import { CheckCircle2, ClipboardList, CircleHelp, Key, Layers, Sparkles, Copy, Check } from 'lucide-react';

export default function SummaryDashboard({ result }) {
  const [activeTab, setActiveTab] = useState('summary');
  const [copied, setCopied] = useState(false);

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const tabs = [
    { id: 'summary', label: 'Executive Summary', icon: Sparkles, color: 'var(--cyan-neon)' },
    { id: 'actions', label: 'Action Items', icon: CheckCircle2, color: 'var(--emerald-neon)' },
    { id: 'decisions', label: 'Key Decisions', icon: Key, color: 'var(--purple-neon)' },
    { id: 'questions', label: 'Open Questions', icon: CircleHelp, color: 'var(--amber-neon)' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Title Card */}
      <div className="glass-card-3d" style={{
        padding: '32px',
        borderLeft: '4px solid var(--cyan-neon)',
        background: 'linear-gradient(135deg, rgba(14, 20, 38, 0.9) 0%, rgba(22, 31, 58, 0.7) 100%)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '20px' }}>
          <div>
            <div className="badge-neon badge-cyan" style={{ marginBottom: '8px' }}>
              VIDEO REPORT READY
            </div>
            <h2 className="font-display" style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff', lineHeight: 1.25 }}>
              {result.title || 'Untitled Video'}
            </h2>
            <p style={{ color: 'var(--cyan-neon)', fontSize: '1.05rem', marginTop: '6px', fontWeight: 500 }}>
              {result.subtitle}
            </p>
          </div>

          <button
            onClick={() => handleCopy(`${result.title}\n\n${result.summary}`)}
            className="btn-cyber-secondary"
            style={{ flexShrink: 0 }}
          >
            {copied ? <Check size={16} color="var(--emerald-neon)" /> : <Copy size={16} />}
            {copied ? 'Copied' : 'Copy All'}
          </button>
        </div>
      </div>

      {/* 3D Tabs Navigation */}
      <div style={{
        display: 'flex',
        gap: '12px',
        padding: '6px',
        background: 'rgba(3, 7, 18, 0.6)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.05)',
        overflowX: 'auto',
      }}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 20px',
                borderRadius: '12px',
                border: 'none',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
                transition: 'all 0.25s ease',
                background: isActive ? 'linear-gradient(135deg, rgba(0, 240, 255, 0.18), rgba(112, 0, 255, 0.25))' : 'transparent',
                color: isActive ? '#fff' : 'var(--text-secondary)',
                border: isActive ? '1px solid rgba(0, 240, 255, 0.35)' : '1px solid transparent',
                boxShadow: isActive ? '0 0 20px rgba(0, 240, 255, 0.2)' : 'none',
                whiteSpace: 'nowrap',
              }}
            >
              <Icon size={18} color={isActive ? tab.color : 'var(--text-muted)'} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content Cards */}
      <div className="glass-card-3d" style={{ padding: '32px', minHeight: '320px' }}>
        {activeTab === 'summary' && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
              <h3 className="font-display" style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--cyan-neon)' }}>
                Executive Video Breakdown
              </h3>
              <button
                onClick={() => handleCopy(result.summary)}
                className="btn-cyber-secondary"
                style={{ padding: '6px 14px', fontSize: '0.8rem' }}
              >
                <Copy size={14} /> Copy Summary
              </button>
            </div>
            <div style={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.7,
              fontSize: '1rem',
              color: 'var(--text-primary)',
            }}>
              {result.summary}
            </div>
          </div>
        )}

        {activeTab === 'actions' && (
          <div>
            <h3 className="font-display" style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--emerald-neon)', marginBottom: '20px' }}>
              Action Items & Assigned Deliverables
            </h3>
            <div style={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.7,
              fontSize: '1rem',
              color: 'var(--text-primary)',
            }}>
              {result.action_items || 'No action items found.'}
            </div>
          </div>
        )}

        {activeTab === 'decisions' && (
          <div>
            <h3 className="font-display" style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--purple-neon)', marginBottom: '20px' }}>
              Key Decisions & Agreements
            </h3>
            <div style={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.7,
              fontSize: '1rem',
              color: 'var(--text-primary)',
            }}>
              {result.key_decisions || 'No key decisions found.'}
            </div>
          </div>
        )}

        {activeTab === 'questions' && (
          <div>
            <h3 className="font-display" style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--amber-neon)', marginBottom: '20px' }}>
              Open Questions & Follow-ups
            </h3>
            <div style={{
              whiteSpace: 'pre-wrap',
              lineHeight: 1.7,
              fontSize: '1rem',
              color: 'var(--text-primary)',
            }}>
              {result.open_questions || 'No open questions found.'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
