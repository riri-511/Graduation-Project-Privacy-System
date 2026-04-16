import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { AlertTriangle, Bell, X } from 'lucide-react';
import { useLanguage } from './LanguageContext';

interface Alert {
  id: number;
  message: string;
  timestamp: Date;
  severity: 'warning' | 'critical';
}

interface AlertsPanelProps {
  peopleCount: number;
  threshold: number;
}

export function AlertsPanel({ peopleCount, threshold }: AlertsPanelProps) {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    if (peopleCount > threshold) {
      const newAlert: Alert = {
        id: Date.now(),
        message: `${t.alerts.thresholdExceeded}: ${peopleCount}/${threshold}`,
        timestamp: new Date(),
        severity: peopleCount > threshold + 2 ? 'critical' : 'warning',
      };
      setAlerts(prev => [newAlert, ...prev].slice(0, 5));
    }
  }, [peopleCount, threshold, t]);

  const dismissAlert = (id: number) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gradient-to-br from-yellow-500/10 to-red-500/10 border border-yellow-500/30 rounded-lg p-6 backdrop-blur-sm"
    >
      <div className="flex items-center gap-3 mb-4">
        <Bell className="text-yellow-400" size={24} />
        <div>
          <h3 className="text-yellow-400 tracking-wide">{t.alerts.title}</h3>
          <p className="text-gray-400 text-xs font-mono mt-1">
            {alerts.length} {t.alerts.activeAlerts}
          </p>
        </div>
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto custom-scrollbar">
        <AnimatePresence mode="popLayout">
          {alerts.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-8 text-gray-500 text-sm font-mono"
            >
              {t.alerts.noAlerts}
            </motion.div>
          ) : (
            alerts.map((alert) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`relative bg-black/40 border rounded p-3 ${
                  alert.severity === 'critical'
                    ? 'border-red-500/40'
                    : 'border-yellow-500/40'
                }`}
              >
                <div className="flex items-start gap-3">
                  <AlertTriangle
                    className={alert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'}
                    size={20}
                  />
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm ${
                      alert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {alert.message}
                    </p>
                    <p className="text-xs text-gray-500 mt-1 font-mono">
                      {alert.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                  <button
                    onClick={() => dismissAlert(alert.id)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <X size={16} />
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
