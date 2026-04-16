import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from './LanguageContext';

interface VideoFeedProps {
  onPeopleCountChange: (count: number) => void;
}

export function VideoFeed({ onPeopleCountChange }: VideoFeedProps) {
  const { t, isRTL } = useLanguage();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [peopleCount, setPeopleCount] = useState(0);
  const [facesAnonymized, setFacesAnonymized] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const attemptsRef = useRef(0);

  useEffect(() => {
    // Start the system first
    const startSystem = async () => {
      try {
        console.log('🚀 Starting system...');
        const response = await fetch('http://localhost:8000/api/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ video_source: 0 }),
        });
        const data = await response.json();
        console.log('✅ System started:', data);
      } catch (error) {
        console.error('❌ Failed to start system:', error);
        setErrorMessage('Cannot connect to Backend API');
      }
    };

    startSystem();

    // WebSocket connection
    const connectWebSocket = () => {
      attemptsRef.current++;
      console.log(`🔌 WebSocket attempt ${attemptsRef.current}`);

      // Close existing connection if any
      if (wsRef.current) {
        wsRef.current.close();
      }

      const ws = new WebSocket('ws://localhost:8000/ws/video');
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('✅ Connected to video stream');
        setIsConnected(true);
        setErrorMessage('');
        attemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'frame' && data.data) {
            const canvas = canvasRef.current;
            if (canvas) {
              const ctx = canvas.getContext('2d');
              if (ctx) {
                const img = new Image();
                img.onload = () => {
                  canvas.width = img.width;
                  canvas.height = img.height;
                  ctx.drawImage(img, 0, 0);
                };
                img.onerror = () => {
                  console.error('❌ Failed to load image from base64');
                  setErrorMessage('Failed to load video frame');
                };
                img.src = `data:image/jpeg;base64,${data.data}`;
              }
            }

            if (data.stats) {
              const count = data.stats.people_count || 0;
              setPeopleCount(count);
              setFacesAnonymized(data.stats.faces_anonymized || 0);
              onPeopleCountChange(count);
            }
          }
        } catch (error) {
          console.error('❌ Error parsing message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setIsConnected(false);
        setErrorMessage('WebSocket connection failed');
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (attemptsRef.current < 5) {
          const delay = Math.min(3000 * attemptsRef.current, 10000);
          console.log(`🔄 Reconnecting in ${delay / 1000}s...`);
          setErrorMessage(`Reconnecting in ${delay / 1000}s...`);
          setTimeout(connectWebSocket, delay);
        } else {
          setErrorMessage('Failed to connect after 5 attempts. Check if Backend is running.');
        }
      };
    };

    // Start connection after 1 second
    setTimeout(connectWebSocket, 1000);

    return () => {
      wsRef.current?.close();
    };
  }, []);

  // Placeholder canvas if not connected
  useEffect(() => {
    if (isConnected) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frame = 0;
    const interval = setInterval(() => {
      ctx.fillStyle = '#0a0a0a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#ff4444';
      ctx.font = '24px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(errorMessage || 'Waiting for Backend...', canvas.width / 2, canvas.height / 2 - 40);

      ctx.fillStyle = '#888';
      ctx.font = '14px monospace';
      ctx.fillText('1. Start Backend: python backend/api_server.py', canvas.width / 2, canvas.height / 2);
      ctx.fillText('2. Wait for connection...', canvas.width / 2, canvas.height / 2 + 25);
      ctx.fillText(`Attempt: ${attemptsRef.current}/5`, canvas.width / 2, canvas.height / 2 + 50);

      const dots = '.'.repeat(frame % 4);
      ctx.fillStyle = '#ff4444';
      ctx.fillText(dots, canvas.width / 2 + 200, canvas.height / 2 - 40);

      frame++;
    }, 500);

    return () => clearInterval(interval);
  }, [isConnected, errorMessage]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="relative rounded-lg overflow-hidden border border-cyan-500/30 shadow-lg shadow-cyan-500/20"
    >
      <canvas
        ref={canvasRef}
        width={800}
        height={500}
        className="w-full h-auto bg-black"
      />

      <div className={`absolute top-4 flex items-center gap-2 ${isRTL ? 'right-4' : 'left-4'}`}>
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`} />
        <span className={`text-xs font-mono ${isConnected ? 'text-red-500' : 'text-gray-500'}`}>
          {isConnected ? (t?.camera?.live || 'LIVE') : 'OFFLINE'}
        </span>
      </div>

      <div className={`absolute top-4 bg-black/60 backdrop-blur-sm px-3 py-1 rounded border border-cyan-500/30 ${isRTL ? 'left-4' : 'right-4'}`}>
        <span className="text-cyan-400 text-xs font-mono">{t?.camera?.sector || 'SECTOR'}</span>
      </div>

      {isConnected && (
        <div className={`absolute top-16 bg-black/60 backdrop-blur-sm px-3 py-1 rounded border border-cyan-500/30 ${isRTL ? 'right-4' : 'left-4'}`}>
          <span className="text-cyan-400 text-xs font-mono">
            People: {peopleCount} | Faces: {facesAnonymized}
          </span>
        </div>
      )}

      <div className={`absolute bottom-4 bg-black/60 backdrop-blur-sm px-3 py-1 rounded border border-green-500/30 ${isRTL ? 'right-4' : 'left-4'}`}>
        <span className="text-green-400 text-xs font-mono">{t?.camera?.privacyActive || 'PRIVACY ACTIVE'}</span>
      </div>

      {!isConnected && errorMessage && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute bottom-16 left-1/2 transform -translate-x-1/2 bg-red-500/20 border border-red-500/40 rounded-lg px-4 py-2 backdrop-blur-sm max-w-md"
        >
          <p className="text-red-400 text-sm font-mono text-center">
            ⚠️ {errorMessage}
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}
