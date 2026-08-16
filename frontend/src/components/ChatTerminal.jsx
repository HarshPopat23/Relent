import React, { useState } from 'react';
import { Bot, MessageSquare, Send, Sparkles, User } from 'lucide-react';

export default function ChatTerminal({ onSendMessage, isChatting, chatHistory }) {
  const [question, setQuestion] = useState('');

  const sampleQuestions = [
    'What are the key specs of RTX 50 series Blackwell architecture?',
    'How does AI help generate extra frames and pixels?',
    'What is the pricing and laptop availability mentioned in the video?',
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || isChatting) return;
    onSendMessage(question.trim());
    setQuestion('');
  };

  return (
    <div className="glass-card-3d" style={{
      padding: '32px',
      border: '1px solid rgba(0, 240, 255, 0.25)',
      boxShadow: '0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 240, 255, 0.12)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #00f0ff 0%, #0077ff 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Bot size={20} color="#030712" />
        </div>
        <div>
          <h3 className="font-display" style={{ fontSize: '1.4rem', fontWeight: 800 }}>
            Neural Transcript Q&A Terminal
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            RAG vector search powered by local Ollama LLM. Answers strictly from video facts.
          </p>
        </div>
      </div>

      {/* Suggested chips */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>PROMPTS:</span>
        {sampleQuestions.map((q, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => {
              setQuestion(q);
              onSendMessage(q);
            }}
            style={{
              fontSize: '0.75rem',
              padding: '5px 12px',
              borderRadius: '8px',
              background: 'rgba(0, 240, 255, 0.05)',
              border: '1px solid rgba(0, 240, 255, 0.2)',
              color: 'var(--cyan-neon)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Conversation Area */}
      <div style={{
        maxHeight: '380px',
        minHeight: '200px',
        overflowY: 'auto',
        padding: '20px',
        background: 'rgba(3, 7, 18, 0.65)',
        borderRadius: '16px',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        marginBottom: '20px',
      }}>
        {chatHistory.length === 0 ? (
          <div style={{ textAlign: 'center', margin: 'auto', color: 'var(--text-muted)' }}>
            <MessageSquare size={32} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
            <p style={{ fontSize: '0.9rem' }}>Ask anything about the video content above.</p>
          </div>
        ) : (
          chatHistory.map((item, index) => (
            <div key={index} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {/* User Question */}
              <div style={{
                alignSelf: 'flex-end',
                maxWidth: '80%',
                padding: '12px 18px',
                borderRadius: '16px 16px 4px 16px',
                background: 'linear-gradient(135deg, rgba(0, 240, 255, 0.2), rgba(112, 0, 255, 0.25))',
                border: '1px solid rgba(0, 240, 255, 0.3)',
                color: '#fff',
                fontSize: '0.95rem',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}>
                <User size={16} color="var(--cyan-neon)" />
                <span>{item.question}</span>
              </div>

              {/* Bot Answer */}
              <div style={{
                alignSelf: 'flex-start',
                maxWidth: '85%',
                padding: '14px 20px',
                borderRadius: '16px 16px 16px 4px',
                background: 'rgba(14, 20, 38, 0.9)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                lineHeight: 1.7,
                boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                  <Bot size={16} color="var(--emerald-neon)" />
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--emerald-neon)', textTransform: 'uppercase' }}>
                    NEXUS AI
                  </span>
                </div>
                <div style={{ whiteSpace: 'pre-wrap' }}>{item.answer}</div>
              </div>
            </div>
          ))
        )}

        {isChatting && (
          <div style={{
            alignSelf: 'flex-start',
            padding: '12px 20px',
            borderRadius: '14px',
            background: 'rgba(14, 20, 38, 0.8)',
            border: '1px solid rgba(0, 240, 255, 0.2)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            color: 'var(--cyan-neon)',
            fontSize: '0.85rem',
          }}>
            <Sparkles size={16} className="anim-pulse-glow" />
            <span>Scanning transcript knowledge graph...</span>
          </div>
        )}
      </div>

      {/* Input bar */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the video..."
          style={{
            flex: 1,
            padding: '14px 18px',
            background: 'rgba(3, 7, 18, 0.8)',
            border: '1px solid rgba(0, 240, 255, 0.3)',
            borderRadius: '12px',
            color: '#fff',
            fontSize: '0.95rem',
            outline: 'none',
          }}
        />
        <button
          type="submit"
          disabled={isChatting || !question.trim()}
          className="btn-cyber-primary"
          style={{ padding: '0 24px' }}
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
