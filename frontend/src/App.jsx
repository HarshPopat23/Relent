import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import Navbar from './components/Navbar';
import InputStation from './components/InputStation';
import ProcessingHUD from './components/ProcessingHUD';
import SummaryDashboard from './components/SummaryDashboard';
import VideoPlayerSection from './components/VideoPlayerSection';
import ReelStudio from './components/ReelStudio';
import ChatTerminal from './components/ChatTerminal';
import ExportBar from './components/ExportBar';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [backendStatus, setBackendStatus] = useState(null);
  const [result, setResult] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isChatting, setIsChatting] = useState(false);
  const [reelResult, setReelResult] = useState(null);
  const [isGeneratingReel, setIsGeneratingReel] = useState(false);

  // Poll backend health
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((res) => res.json())
      .then((data) => setBackendStatus(data))
      .catch((err) => console.log('Backend health check:', err));
  }, []);

  // Process Video Handler
  const handleProcessVideo = async (payload) => {
    setIsProcessing(true);
    setErrorMessage(null);
    setResult(null);
    setChatHistory([]);
    setReelResult(null);

    try {
      let res;
      if (payload.type === 'file') {
        const formData = new FormData();
        formData.append('file', payload.file);
        formData.append('language', payload.language);
        res = await fetch(`${API_BASE}/api/process`, {
          method: 'POST',
          body: formData,
        });
      } else {
        res = await fetch(`${API_BASE}/api/process`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source: payload.source,
            language: payload.language,
          }),
        });
      }

      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || 'Failed to process video.');
      }

      setResult(data);
      // Trigger cyber celebration confetti
      try {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ['#00f0ff', '#9d4edd', '#00ff9d'],
        });
      } catch (e) {}
    } catch (err) {
      setErrorMessage(err.message || 'An error occurred during video analysis.');
    } finally {
      setIsProcessing(false);
    }
  };

  // Chat RAG Handler
  const handleSendMessage = async (question) => {
    setIsChatting(true);
    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || 'Failed to get answer.');
      }
      setChatHistory(data.history || []);
    } catch (err) {
      alert(`Chat error: ${err.message}`);
    } finally {
      setIsChatting(false);
    }
  };

  // Reel Generation Handler
  const handleGenerateReel = async (reelRequest) => {
    setIsGeneratingReel(true);
    setReelResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/reel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request: reelRequest }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        setReelResult({ error: data.error || 'Failed to cut reel.' });
      } else {
        setReelResult({
          script: data.script,
          reel_url: data.reel_url ? `${API_BASE}${data.reel_url}` : null,
          error: null,
        });
      }
    } catch (err) {
      setReelResult({ error: err.message || 'Error communicating with reel service.' });
    } finally {
      setIsGeneratingReel(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      <div className="perspective-grid" />

      {/* Navbar */}
      <Navbar backendStatus={backendStatus} />

      {/* Main Container */}
      <main style={{ flex: 1, maxWidth: '1280px', width: '100%', margin: '0 auto', padding: '24px 20px 80px', position: 'relative', zIndex: 1 }}>
        {/* Error Alert */}
        {errorMessage && (
          <div style={{
            maxWidth: '900px',
            margin: '0 auto 24px',
            padding: '16px 24px',
            borderRadius: '16px',
            background: 'rgba(255, 51, 102, 0.15)',
            border: '1px solid var(--rose-neon)',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 0 30px rgba(255, 51, 102, 0.3)',
          }}>
            <div>
              <strong>Pipeline Error:</strong> {errorMessage}
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#fff',
                cursor: 'pointer',
                fontWeight: 700,
                fontSize: '1rem',
              }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Input Station */}
        <InputStation onProcess={handleProcessVideo} isProcessing={isProcessing} />

        {/* Live Processing HUD */}
        {isProcessing && <ProcessingHUD />}

        {/* Results Matrix */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', marginTop: '40px' }}>
            {/* Executive Summary */}
            <SummaryDashboard result={result} />

            {/* Video Player & Synchronized Transcript */}
            <VideoPlayerSection
              videoUrl={result.video_url ? `${API_BASE}${result.video_url}` : null}
              transcript={result.transcript}
            />

            {/* AI Reel Studio */}
            <ReelStudio
              onGenerateReel={handleGenerateReel}
              isGeneratingReel={isGeneratingReel}
              reelResult={reelResult}
            />

            {/* AI Chat Terminal */}
            <ChatTerminal
              onSendMessage={handleSendMessage}
              isChatting={isChatting}
              chatHistory={chatHistory}
            />

            {/* Export & Download Center */}
            <ExportBar apiBase={API_BASE} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        textAlign: 'center',
        padding: '24px',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        color: 'var(--text-muted)',
        fontSize: '0.85rem',
        background: 'rgba(6, 8, 16, 0.95)',
        position: 'relative',
        zIndex: 1,
      }}>
        NEXUS AI VIDEO AGENT &copy; 2026 &bull; Powered by Whisper, Chroma Vector DB, Ollama Qwen & FFmpeg
      </footer>
    </div>
  );
}
