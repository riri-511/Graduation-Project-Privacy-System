import { motion } from 'motion/react';
import { Languages } from 'lucide-react';
import { useLanguage } from './LanguageContext';

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex items-center gap-2 bg-black/40 backdrop-blur-sm border border-cyan-500/30 rounded-lg p-1"
    >
      <Languages className="text-cyan-400 ml-2" size={18} />
      <button
        onClick={() => setLanguage('en')}
        className={`px-3 py-1.5 rounded transition-all text-sm font-mono ${
          language === 'en'
            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
            : 'text-gray-400 hover:text-cyan-400'
        }`}
      >
        EN
      </button>
      <button
        onClick={() => setLanguage('ar')}
        className={`px-3 py-1.5 rounded transition-all text-sm font-mono ${
          language === 'ar'
            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
            : 'text-gray-400 hover:text-cyan-400'
        }`}
      >
        AR
      </button>
    </motion.div>
  );
}
