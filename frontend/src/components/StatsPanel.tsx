import { motion } from 'motion/react';
import { Users, Activity, Shield, Eye } from 'lucide-react';
import { useLanguage } from './LanguageContext';

interface StatsPanelProps {
  peopleCount: number;
  threshold: number;
}

export function StatsPanel({ peopleCount, threshold }: StatsPanelProps) {
  const { t } = useLanguage();
  
  const stats = [
    {
      icon: Users,
      label: t.stats.detected,
      value: peopleCount,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/30',
    },
    {
      icon: Activity,
      label: t.stats.threshold,
      value: threshold,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30',
    },
    {
      icon: Shield,
      label: t.stats.anonymized,
      value: peopleCount,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30',
    },
    {
      icon: Eye,
      label: t.stats.privacy,
      value: '100%',
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`relative ${stat.bgColor} border ${stat.borderColor} rounded-lg p-4 backdrop-blur-sm overflow-hidden`}
        >
          {/* Holographic gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
          
          <div className="relative flex items-start justify-between">
            <div>
              <p className="text-gray-400 text-xs mb-1 font-mono">{stat.label}</p>
              <motion.p
                key={`${stat.label}-${stat.value}`}
                initial={{ scale: 1.2 }}
                animate={{ scale: 1 }}
                className={`${stat.color} text-2xl tracking-wider font-mono`}
              >
                {stat.value}
              </motion.p>
            </div>
            <stat.icon className={`${stat.color} opacity-40`} size={24} />
          </div>

          {/* Animated border effect */}
          <motion.div
            className={`absolute bottom-0 left-0 h-0.5 ${stat.bgColor.replace('/10', '')}`}
            initial={{ width: '0%' }}
            animate={{ width: '100%' }}
            transition={{ duration: 1, delay: index * 0.1 }}
          />
        </motion.div>
      ))}
    </div>
  );
}
