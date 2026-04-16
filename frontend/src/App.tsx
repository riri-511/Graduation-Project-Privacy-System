import { useState } from 'react';
import { motion } from 'motion/react';
import { VideoFeed } from './components/VideoFeed';
import { StatsPanel } from './components/StatsPanel';
import { EncryptionStatus } from './components/EncryptionStatus';
import { RecordingStatus } from './components/RecordingStatus';
import { AlertsPanel } from './components/AlertsPanel';
import { SearchPage } from './components/SearchPage'; // ✅ تمت الإضافة
import { LanguageProvider, useLanguage } from './components/LanguageContext';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { Shield, Activity, Search, LayoutDashboard } from 'lucide-react'; // ✅ تمت إضافة الأيقونات
import { Button } from './components/ui/button'; // ✅ تأكد من وجود هذا

function AppContent() {
  const { t, isRTL } = useLanguage();
  const [peopleCount, setPeopleCount] = useState(0);
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'search'>('dashboard'); // ✅ حالة للتنقل بين الصفحات
  const threshold = 5;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white p-6 relative overflow-hidden" dir={isRTL ? 'rtl' : 'ltr'}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute top-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, 50, 0],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
        <motion.div
          className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"
          animate={{
            x: [0, -100, 0],
            y: [0, -50, 0],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: 'linear',
          }}
        />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Shield className="text-cyan-400" size={40} />
                <motion.div
                  className="absolute inset-0 bg-cyan-400/20 rounded-full blur-xl"
                  animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.5, 0.8, 0.5],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                  }}
                />
              </div>
              <div>
                <h1 className="text-3xl tracking-wide bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  {t.header.title}
                </h1>
                <p className="text-gray-400 mt-1 text-sm font-mono">
                  {t.header.subtitle}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <div className="flex items-center gap-2 bg-green-500/20 border border-green-500/30 rounded-lg px-4 py-2">
                <Activity className="text-green-400" size={20} />
                <span className="text-green-400 font-mono">{t.header.systemOnline}</span>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex gap-2">
            <Button
              onClick={() => setCurrentPage('dashboard')}
              variant={currentPage === 'dashboard' ? 'default' : 'outline'}
              className={
                currentPage === 'dashboard'
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white border-0'
                  : 'border-cyan-500/30 text-gray-300 hover:bg-slate-800/50 hover:text-cyan-400 hover:border-cyan-400'
              }
            >
              <LayoutDashboard size={16} className={isRTL ? 'ml-2' : 'mr-2'} />
              {t.navigation.dashboard}
            </Button>
            <Button
              onClick={() => setCurrentPage('search')}
              variant={currentPage === 'search' ? 'default' : 'outline'}
              className={
                currentPage === 'search'
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white border-0'
                  : 'border-cyan-500/30 text-gray-300 hover:bg-slate-800/50 hover:text-cyan-400 hover:border-cyan-400'
              }
            >
              <Search size={16} className={isRTL ? 'ml-2' : 'mr-2'} />
              {t.navigation.search}
            </Button>
          </div>
        </motion.header>

        {/* Conditional Page Rendering */}
        {currentPage === 'dashboard' ? (
          <>
            {/* Stats Panel */}
            <div className="mb-6">
              <StatsPanel peopleCount={peopleCount} threshold={threshold} />
            </div>

            {/* Main Content Grid */}
            <div className="grid lg:grid-cols-3 gap-6 mb-6">
              {/* Video Feed - Takes 2 columns */}
              <div className="lg:col-span-2">
                <VideoFeed onPeopleCountChange={setPeopleCount} />
              </div>

              {/* Side Panel */}
              <div className="space-y-6">
                <EncryptionStatus />
                <RecordingStatus />
              </div>
            </div>

            {/* Alerts Panel */}
            <AlertsPanel peopleCount={peopleCount} threshold={threshold} />
          </>
        ) : (
          <SearchPage /> // ✅ صفحة البحث تظهر هنا
        )}

        {/* Footer Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 text-center text-gray-500 text-xs font-mono"
        >
          <p>{t.footer}</p>
        </motion.div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
}