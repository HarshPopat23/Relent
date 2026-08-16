import React from 'react';
import { Download, FileCode, FileDown, FileText } from 'lucide-react';

export default function ExportBar({ apiBase = 'http://127.0.0.1:8000' }) {
  return (
    <div className="glass-card-3d" style={{
      padding: '24px 32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px',
      border: '1px solid rgba(0, 240, 255, 0.2)',
    }}>
      <div>
        <h4 className="font-display" style={{ fontSize: '1.1rem', fontWeight: 700 }}>
          Export & Intelligence Artifacts
        </h4>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Download formatted notes, full timestamp transcript, or PDF meeting brief.
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        <a
          href={`${apiBase}/api/download/pdf`}
          download="video_intelligence_report.pdf"
          className="btn-cyber-primary"
          style={{ textDecoration: 'none', padding: '10px 20px', fontSize: '0.85rem' }}
        >
          <FileDown size={16} /> Download Full PDF
        </a>

        <a
          href={`${apiBase}/api/download/markdown`}
          download="video_notes.md"
          className="btn-cyber-secondary"
          style={{ textDecoration: 'none', padding: '10px 18px', fontSize: '0.85rem' }}
        >
          <FileCode size={16} /> Markdown (.md)
        </a>

        <a
          href={`${apiBase}/api/download/summary`}
          download="summary.txt"
          className="btn-cyber-secondary"
          style={{ textDecoration: 'none', padding: '10px 18px', fontSize: '0.85rem' }}
        >
          <FileText size={16} /> Summary (.txt)
        </a>

        <a
          href={`${apiBase}/api/download/transcript`}
          download="transcript.txt"
          className="btn-cyber-secondary"
          style={{ textDecoration: 'none', padding: '10px 18px', fontSize: '0.85rem' }}
        >
          <FileText size={16} /> Transcript (.txt)
        </a>
      </div>
    </div>
  );
}
