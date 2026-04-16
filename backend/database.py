"""
نظام قاعدة البيانات لحفظ السجلات والإحصائيات
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_path: str = 'data/surveillance.db'):
        """
        تهيئة قاعدة البيانات
        
        Args:
            db_path: مسار ملف قاعدة البيانات
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self._create_tables()
        logger.info(f"✅ تم الاتصال بقاعدة البيانات: {db_path}")
    
    def _create_tables(self):
        """إنشاء الجداول"""
        
        # جدول الجلسات
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            total_frames INTEGER DEFAULT 0,
            encrypted_file TEXT,
            status TEXT DEFAULT 'active'
        )
        ''')
        
        # جدول الكشوفات
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            frame_number INTEGER,
            person_count INTEGER,
            track_ids TEXT,
            anonymized_faces INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        ''')
        
        # جدول الإشعارات
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            alert_type TEXT,
            message TEXT,
            severity TEXT DEFAULT 'info',
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        ''')
        
        # جدول الإحصائيات
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            date TEXT NOT NULL,
            max_people INTEGER DEFAULT 0,
            avg_people REAL DEFAULT 0,
            total_detections INTEGER DEFAULT 0,
            total_faces_anonymized INTEGER DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
        ''')
        
        self.conn.commit()
        logger.info("📊 تم إنشاء/تحميل جداول قاعدة البيانات")
    
    # ===== إدارة الجلسات =====
    
    def create_session(self, session_id: str) -> int:
        """إنشاء جلسة جديدة"""
        try:
            self.cursor.execute('''
            INSERT INTO sessions (session_id, start_time, status)
            VALUES (?, ?, 'active')
            ''', (session_id, datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"✅ تم إنشاء جلسة: {session_id}")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ الجلسة موجودة مسبقاً: {session_id}")
            return None
    
    def end_session(self, session_id: str, encrypted_file: str = None):
        """إنهاء الجلسة"""
        self.cursor.execute('''
        UPDATE sessions 
        SET end_time = ?, status = 'completed', encrypted_file = ?
        WHERE session_id = ?
        ''', (datetime.now().isoformat(), encrypted_file, session_id))
        self.conn.commit()
        logger.info(f"✅ تم إنهاء الجلسة: {session_id}")
    
    def get_active_sessions(self) -> List[Dict]:
        """الحصول على الجلسات النشطة"""
        self.cursor.execute('''
        SELECT * FROM sessions WHERE status = 'active'
        ''')
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # ===== تسجيل الكشوفات =====
    
    def log_detection(self, session_id: str, frame_number: int, 
                     person_count: int, track_ids: List[int], 
                     anonymized_faces: int = 0):
        """تسجيل كشف"""
        self.cursor.execute('''
        INSERT INTO detections 
        (session_id, timestamp, frame_number, person_count, track_ids, anonymized_faces)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            datetime.now().isoformat(),
            frame_number,
            person_count,
            json.dumps(track_ids),
            anonymized_faces
        ))
        self.conn.commit()
    
    def get_recent_detections(self, session_id: str, limit: int = 100) -> List[Dict]:
        """الحصول على آخر الكشوفات"""
        self.cursor.execute('''
        SELECT * FROM detections 
        WHERE session_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (session_id, limit))
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # ===== الإشعارات =====
    
    def create_alert(self, session_id: str, alert_type: str, 
                    message: str, severity: str = 'info'):
        """إنشاء إشعار"""
        self.cursor.execute('''
        INSERT INTO alerts (session_id, timestamp, alert_type, message, severity)
        VALUES (?, ?, ?, ?, ?)
        ''', (session_id, datetime.now().isoformat(), alert_type, message, severity))
        self.conn.commit()
        logger.info(f"🔔 إشعار جديد [{severity}]: {message}")
    
    def get_alerts(self, session_id: str, severity: str = None) -> List[Dict]:
        """الحصول على الإشعارات"""
        if severity:
            self.cursor.execute('''
            SELECT * FROM alerts 
            WHERE session_id = ? AND severity = ?
            ORDER BY timestamp DESC
            ''', (session_id, severity))
        else:
            self.cursor.execute('''
            SELECT * FROM alerts 
            WHERE session_id = ?
            ORDER BY timestamp DESC
            ''', (session_id,))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # ===== الإحصائيات =====
    
    def update_statistics(self, session_id: str, max_people: int, 
                         avg_people: float, total_detections: int,
                         total_faces: int):
        """تحديث إحصائيات الجلسة"""
        today = datetime.now().date().isoformat()
        
        self.cursor.execute('''
        INSERT OR REPLACE INTO statistics 
        (session_id, date, max_people, avg_people, total_detections, total_faces_anonymized)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, today, max_people, avg_people, total_detections, total_faces))
        self.conn.commit()
    
    def get_statistics(self, session_id: str) -> Optional[Dict]:
        """الحصول على إحصائيات الجلسة"""
        self.cursor.execute('''
        SELECT * FROM statistics WHERE session_id = ?
        ORDER BY date DESC LIMIT 1
        ''', (session_id,))
        
        row = self.cursor.fetchone()
        if row:
            columns = [desc[0] for desc in self.cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_all_statistics(self) -> List[Dict]:
        """الحصول على جميع الإحصائيات"""
        self.cursor.execute('SELECT * FROM statistics ORDER BY date DESC')
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    # ===== استعلامات متقدمة =====
    
    def get_hourly_stats(self, session_id: str) -> List[Dict]:
        """إحصائيات ساعية"""
        self.cursor.execute('''
        SELECT 
            strftime('%H:00', timestamp) as hour,
            AVG(person_count) as avg_people,
            MAX(person_count) as max_people,
            COUNT(*) as detections
        FROM detections
        WHERE session_id = ?
        GROUP BY hour
        ORDER BY hour
        ''', (session_id,))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def get_peak_times(self, session_id: str, limit: int = 5) -> List[Dict]:
        """أوقات الذروة"""
        self.cursor.execute('''
        SELECT timestamp, person_count, track_ids
        FROM detections
        WHERE session_id = ?
        ORDER BY person_count DESC
        LIMIT ?
        ''', (session_id, limit))
        
        columns = [desc[0] for desc in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def __del__(self):
        """إغلاق الاتصال"""
        if hasattr(self, 'conn'):
            self.conn.close()
            logger.info("🔌 تم إغلاق الاتصال بقاعدة البيانات")


# مثال للاستخدام
if __name__ == "__main__":
    # تهيئة قاعدة البيانات
    db = DatabaseManager('data/surveillance.db')
    
    # إنشاء جلسة
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    db.create_session(session_id)
    
    # تسجيل بعض الكشوفات
    print("📝 تسجيل كشوفات تجريبية...")
    for i in range(10):
        db.log_detection(
            session_id=session_id,
            frame_number=i * 30,
            person_count=5 + (i % 3),
            track_ids=[1, 2, 3, 4, 5],
            anonymized_faces=5 + (i % 3)
        )
    
    # إنشاء إشعار
    db.create_alert(
        session_id=session_id,
        alert_type='high_occupancy',
        message='تجاوز عدد الأشخاص الحد المسموح',
        severity='warning'
    )
    
    # الحصول على البيانات
    print("\n📊 الجلسات النشطة:")
    sessions = db.get_active_sessions()
    for session in sessions:
        print(f"  - {session['session_id']}: {session['start_time']}")
    
    print("\n📈 آخر الكشوفات:")
    detections = db.get_recent_detections(session_id, limit=5)
    for det in detections:
        print(f"  - Frame {det['frame_number']}: {det['person_count']} أشخاص")
    
    print("\n🔔 الإشعارات:")
    alerts = db.get_alerts(session_id)
    for alert in alerts:
        print(f"  - [{alert['severity']}] {alert['message']}")
    
    # تحديث الإحصائيات
    db.update_statistics(
        session_id=session_id,
        max_people=8,
        avg_people=6.2,
        total_detections=10,
        total_faces=62
    )
    
    print("\n📊 الإحصائيات:")
    stats = db.get_statistics(session_id)
    if stats:
        print(f"  - أقصى عدد: {stats['max_people']}")
        print(f"  - المتوسط: {stats['avg_people']:.1f}")
        print(f"  - إجمالي الوجوه المخفية: {stats['total_faces_anonymized']}")
    
    # إنهاء الجلسة
    db.end_session(session_id, encrypted_file='data/encrypted/test.enc')
    
    print("\n✅ تم الانتهاء من الاختبار!")