import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { Video, HardDrive, Clock } from 'lucide-react';
import { useLanguage } from './LanguageContext';

export function RecordingStatus() {
  const { t } = useLanguage();
  const [timestamp, setTimestamp] = useState(new Date());
  const [duration, setDuration] = useState(0);
  const [storageUsed, setStorageUsed] = useState(2.4);

  useEffect(() => {
    const interval = setInterval(() => {
      setTimestamp(new Date());
      setDuration(prev => prev + 1);
      setStorageUsed(prev => prev + 0.001);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const formatDuration = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border border-red-500/30 rounded-lg p-6 backdrop-blur-sm relative overflow-hidden"
    >
      {/* Animated background pulse */}
      <motion.div
        className="absolute inset-0 bg-red-500/5"
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
        }}
      />

      <div className="relative">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative">
            <Video className="text-red-400" size={24} />
            <motion.div
              className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [1, 0.5, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
              }}
            />
          </div>
          <div>
            <h3 className="text-red-400 tracking-wide">{t.recording.title}</h3>
            <p className="text-gray-400 text-xs font-mono mt-1">{t.recording.active}</p>
          </div>
        </div>

        <div className="space-y-3">
          {/* Timestamp */}
          <div className="bg-black/40 rounded border border-red-500/20 p-3">
            <div className="flex items-center gap-2 mb-1">
              <Clock size={14} className="text-gray-400" />
              <span className="text-gray-400 text-xs font-mono">{t.recording.timestamp}</span>
            </div>
            <p className="text-red-400 font-mono text-sm">
              {timestamp.toLocaleDateString()} {timestamp.toLocaleTimeString()}
            </p>
          </div>

          {/* Duration */}
          <div className="flex items-center justify-between">
            <span className="text-gray-400 text-xs font-mono">{t.recording.duration}</span>
            <span className="text-red-400 font-mono">{formatDuration(duration)}</span>
          </div>

          {/* Storage */}
          <div>
            <div className="flex items-center justify-between text-xs mb-2">
              <div className="flex items-center gap-2">
                <HardDrive size={14} className="text-gray-400" />
                <span className="text-gray-400 font-mono">{t.recording.storageUsed}</span>
              </div>
              <span className="text-orange-400 font-mono">{storageUsed.toFixed(2)} GB</span>
            </div>
            <div className="h-1.5 bg-black/40 rounded-full overflow-hidden border border-orange-500/20">
              <motion.div
                className="h-full bg-gradient-to-r from-orange-500 to-red-500"
                initial={{ width: '0%' }}
                animate={{ width: `${(storageUsed / 10) * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
