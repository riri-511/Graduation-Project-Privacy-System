import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { Lock, CheckCircle, AlertCircle } from 'lucide-react';
import { useLanguage } from './LanguageContext';

export function EncryptionStatus() {
  const { t } = useLanguage();
  const [status, setStatus] = useState<'encrypting' | 'encrypted' | 'verified'>('encrypting');
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Simulate encryption process
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          setStatus('encrypted');
          setTimeout(() => setStatus('verified'), 500);
          return 100;
        }
        return prev + 2;
      });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-lg p-6 backdrop-blur-sm relative overflow-hidden"
    >
      {/* Animated background */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-blue-500/5"
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: 'linear',
        }}
      />

      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Lock className="text-cyan-400" size={24} />
              {status === 'verified' && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute -top-1 -right-1"
                >
                  <CheckCircle className="text-green-400" size={16} />
                </motion.div>
              )}
            </div>
            <div>
              <h3 className="text-cyan-400 tracking-wide">{t.encryption.title}</h3>
              <p className="text-gray-400 text-xs font-mono mt-1">{t.encryption.protocol}</p>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full border text-xs font-mono ${
            status === 'verified'
              ? 'bg-green-500/20 border-green-500/30 text-green-400'
              : status === 'encrypted'
              ? 'bg-blue-500/20 border-blue-500/30 text-blue-400'
              : 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400'
          }`}>
            {status === 'verified' ? t.encryption.verified : status === 'encrypted' ? t.encryption.encrypted : t.encryption.encrypting}
          </div>
        </div>

        {/* Progress bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-400 mb-2 font-mono">
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="h-2 bg-black/40 rounded-full overflow-hidden border border-cyan-500/20">
            <motion.div
              className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
              initial={{ width: '0%' }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        {/* Encryption details */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400 font-mono">{t.encryption.keyLength}</span>
            <span className="text-cyan-400 font-mono">256-bit</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400 font-mono">Protocol</span>
            <span className="text-cyan-400 font-mono">TLS 1.3</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400 font-mono">{t.encryption.dataIntegrity}</span>
            <div className="flex items-center gap-1">
              <CheckCircle size={12} className="text-green-400" />
              <span className="text-green-400 font-mono">{t.encryption.verified}</span>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
