import { createContext, useContext, useState, ReactNode } from 'react';

type Language = 'en' | 'ar';

interface Translations {
  // أضفنا navigation و search هنا
  navigation: {
    dashboard: string;
    search: string;
  };
  search: {
    title: string;
    searchType: string;
    recorded: string;
    live: string;
    dateTimeRange: string;
    from: string;
    to: string;
    filters: string;
    numPeople: string;
    sessionId: string;
    trackId: string;
    searchButton: string;
    clearButton: string;
    results: string;
    found: string;
    frame: string;
    viewDetails: string;
    exportResults: string;
    noResults: string;
  };
  header: {
    title: string;
    subtitle: string;
    systemOnline: string;
  };
  stats: {
    detected: string;
    threshold: string;
    anonymized: string;
    privacy: string;
  };
  encryption: {
    title: string;
    protocol: string;
    verified: string;
    encrypted: string;
    encrypting: string;
    keyLength: string;
    dataIntegrity: string;
  };
  recording: {
    title: string;
    active: string;
    timestamp: string;
    duration: string;
    storageUsed: string;
  };
  alerts: {
    title: string;
    activeAlerts: string;
    noAlerts: string;
    thresholdExceeded: string;
  };
  camera: {
    live: string;
    sector: string;
    privacyMode: string;
    privacyActive: string;
  };
  footer: string;
}

const translations: Record<Language, Translations> = {
  en: {
    // أضفنا navigation و search
    navigation: {
      dashboard: 'Dashboard',
      search: 'Search',
    },
    search: {
      title: 'Advanced Search',
      searchType: 'Search Type',
      recorded: 'Recorded Sessions',
      live: 'Live Tracking',
      dateTimeRange: 'Date/Time Range',
      from: 'From',
      to: 'To',
      filters: 'Filters',
      numPeople: 'Number of People',
      sessionId: 'Session ID',
      trackId: 'Track ID',
      searchButton: 'Search',
      clearButton: 'Clear',
      results: 'Search Results',
      found: 'found',
      frame: 'Frame',
      viewDetails: 'View Details',
      exportResults: 'Export Results',
      noResults: 'No results found',
    },
    header: {
      title: 'Security Monitoring System',
      subtitle: 'People Tracking • Anonymization • Encryption',
      systemOnline: 'System Online',
    },
    stats: {
      detected: 'Detected',
      threshold: 'Threshold',
      anonymized: 'Anonymized',
      privacy: 'Privacy',
    },
    encryption: {
      title: 'Encryption Status',
      protocol: 'AES-256-GCM',
      verified: 'VERIFIED',
      encrypted: 'ENCRYPTED',
      encrypting: 'ENCRYPTING',
      keyLength: 'Key Length',
      dataIntegrity: 'Data Integrity',
    },
    recording: {
      title: 'Recording Active',
      active: '1080p • 30fps',
      timestamp: 'Timestamp',
      duration: 'Duration',
      storageUsed: 'Storage Used',
    },
    alerts: {
      title: 'System Alerts',
      activeAlerts: 'active alert',
      noAlerts: 'No active alerts',
      thresholdExceeded: 'Occupancy threshold exceeded',
    },
    camera: {
      live: 'LIVE',
      sector: 'CAM-01 | SECTOR-A',
      privacyMode: 'Privacy Mode',
      privacyActive: 'PRIVACY MODE: ACTIVE',
    },
    footer: '© 2025 Security Monitoring System • All data encrypted and anonymized',
  },
  ar: {
    // أضفنا navigation و search
    navigation: {
      dashboard: 'لوحة التحكم',
      search: 'بحث',
    },
    search: {
      title: 'بحث متقدم',
      searchType: 'نوع البحث',
      recorded: 'الجلسات المسجلة',
      live: 'التتبع المباشر',
      dateTimeRange: 'نطاق التاريخ/الوقت',
      from: 'من',
      to: 'إلى',
      filters: 'مرشحات',
      numPeople: 'عدد الأشخاص',
      sessionId: 'معرف الجلسة',
      trackId: 'معرف المسار',
      searchButton: 'بحث',
      clearButton: 'مسح',
      results: 'نتائج البحث',
      found: 'تم العثور على',
      frame: 'إطار',
      viewDetails: 'عرض التفاصيل',
      exportResults: 'تصدير النتائج',
      noResults: 'لم يتم العثور على نتائج',
    },
    header: {
      title: 'نظام المراقبة الأمنية',
      subtitle: 'تتبع الأشخاص • إخفاء الهوية • التشفير',
      systemOnline: 'النظام متصل',
    },
    stats: {
      detected: 'المكتشف',
      threshold: 'الحد الأقصى',
      anonymized: 'مجهول الهوية',
      privacy: 'الخصوصية',
    },
    encryption: {
      title: 'حالة التشفير',
      protocol: 'AES-256-GCM',
      verified: 'تم التحقق',
      encrypted: 'مشفر',
      encrypting: 'جاري التشفير',
      keyLength: 'طول المفتاح',
      dataIntegrity: 'سلامة البيانات',
    },
    recording: {
      title: 'التسجيل نشط',
      active: '1080p • 30fps',
      timestamp: 'الطابع الزمني',
      duration: 'المدة',
      storageUsed: 'المساحة المستخدمة',
    },
    alerts: {
      title: 'تنبيهات النظام',
      activeAlerts: 'تنبيه نشط',
      noAlerts: 'لا توجد تنبيهات نشطة',
      thresholdExceeded: 'تم تجاوز الحد الأقصى للأشخاص',
    },
    camera: {
      live: 'مباشر',
      sector: 'كاميرا-01 | القطاع-أ',
      privacyMode: 'وضع الخصوصية',
      privacyActive: 'وضع الخصوصية: نشط',
    },
    footer: '© 2025 نظام المراقبة الأمنية • جميع البيانات مشفرة ومجهولة الهوية',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
  isRTL: boolean;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  const value: LanguageContextType = {
    language,
    setLanguage,
    t: translations[language],
    isRTL: language === 'ar',
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}