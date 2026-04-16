"""
Backend API Server للواجهة React
يربط الواجهة مع نظام الكشف والتتبع والتشفير
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import cv2
import numpy as np
import asyncio
import json
from datetime import datetime
from typing import List
import base64
import logging

# استيراد المكونات
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.detector import PersonDetector
from backend.tracker import PersonTracker
from backend.anonymizer import FaceAnonymizer
from backend.encryption import VideoEncryptor
from backend.database import DatabaseManager

# إعداد Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(title="Security Monitoring API")

# CORS للسماح للـ React بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# النظام العام
class SurveillanceSystem:
    def __init__(self):
        self.detector = PersonDetector(model_path='yolov8n.pt', conf_threshold=0.5)
        self.tracker = PersonTracker(max_age=30, n_init=3)
        self.anonymizer = FaceAnonymizer(method='blur', blur_intensity=51)
        self.encryptor = VideoEncryptor()
        self.db = DatabaseManager()
        
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.db.create_session(self.session_id)
        
        self.is_running = False
        self.video_source = 0
        self.cap = None
        
        self.frame_count = 0
        self.people_count = 0
        self.faces_anonymized = 0
        self.track_ids = []
        
        logger.info(f"✅ System initialized - Session: {self.session_id}")
    
    def start(self, video_source=0):
        """بدء النظام"""
        self.video_source = video_source
        self.cap = cv2.VideoCapture(video_source)
        
        if not self.cap.isOpened():
            logger.error("❌ Failed to open video source")
            return False
        
        self.is_running = True
        logger.info(f"▶️ System started - Source: {video_source}")
        return True
    
    def stop(self):
        """إيقاف النظام"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.db.end_session(self.session_id)
        logger.info("⏹️ System stopped")
    
    def process_frame(self):
        """معالجة إطار واحد"""
        if not self.cap or not self.is_running:
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        # 1. الكشف
        detections, _ = self.detector.detect(frame)
        
        # 2. التتبع
        tracks, tracked_frame = self.tracker.update(detections, frame)
        
        # 3. إخفاء الوجوه
        anonymized_frame, face_count = self.anonymizer.anonymize(tracked_frame)
        
        # 4. تحديث الإحصائيات
        self.frame_count += 1
        self.people_count = len(tracks)
        self.faces_anonymized = face_count
        self.track_ids = [t['id'] for t in tracks]
        
        # 5. رسم المعلومات على الإطار
        info_text = f"People: {self.people_count} | Faces: {face_count} | Frame: {self.frame_count}"
        cv2.putText(anonymized_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # إضافة مربعات التتبع
        for track in tracks:
            x1, y1, x2, y2 = track['bbox']
            track_id = track['id']
            color = track['color']
            
            # رسم المربع
            cv2.rectangle(anonymized_frame, (x1, y1), (x2, y2), color, 2)
            
            # ID Label
            cv2.putText(anonymized_frame, f"ID: {track_id}", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 6. تسجيل في قاعدة البيانات (كل ثانية)
        if self.frame_count % 30 == 0:
            self.db.log_detection(
                session_id=self.session_id,
                frame_number=self.frame_count,
                person_count=self.people_count,
                track_ids=self.track_ids,
                anonymized_faces=face_count
            )
        
        # 7. إعداد البيانات للإرسال
        stats = {
            'people_count': self.people_count,
            'faces_anonymized': face_count,
            'frame_count': self.frame_count,
            'track_ids': self.track_ids,
            'timestamp': datetime.now().isoformat()
        }
        
        return anonymized_frame, stats

# النظام العام - Instance واحد
system = SurveillanceSystem()

# ===== API Endpoints =====

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Security Monitoring API",
        "version": "1.0.0",
        "status": "online",
        "session_id": system.session_id
    }

@app.post("/api/start")
async def start_system(video_source: int = 0):
    """بدء النظام"""
    success = system.start(video_source)
    return {
        "success": success,
        "message": "System started" if success else "Failed to start",
        "session_id": system.session_id
    }

@app.post("/api/stop")
async def stop_system():
    """إيقاف النظام"""
    system.stop()
    return {
        "success": True,
        "message": "System stopped"
    }

@app.get("/api/status")
async def get_status():
    """الحصول على حالة النظام"""
    return {
        "is_running": system.is_running,
        "session_id": system.session_id,
        "frame_count": system.frame_count,
        "people_count": system.people_count,
        "faces_anonymized": system.faces_anonymized,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stats")
async def get_stats():
    """الحصول على الإحصائيات"""
    stats = system.db.get_statistics(system.session_id)
    return {
        "current": {
            "people_count": system.people_count,
            "faces_anonymized": system.faces_anonymized,
            "frame_count": system.frame_count
        },
        "session": stats if stats else {}
    }

@app.get("/api/detections")
async def get_detections(limit: int = 10):
    """الحصول على آخر الكشوفات"""
    detections = system.db.get_recent_detections(system.session_id, limit)
    return {
        "detections": detections,
        "count": len(detections)
    }

@app.get("/api/alerts")
async def get_alerts():
    """الحصول على الإشعارات"""
    alerts = system.db.get_alerts(system.session_id)
    return {
        "alerts": alerts,
        "count": len(alerts)
    }

@app.post("/api/alert")
async def create_alert(alert_type: str, message: str, severity: str = "info"):
    """إنشاء إشعار جديد"""
    system.db.create_alert(
        session_id=system.session_id,
        alert_type=alert_type,
        message=message,
        severity=severity
    )
    return {
        "success": True,
        "message": "Alert created"
    }

# ===== Search Endpoints (NEW) =====

@app.post("/api/search")
async def search_detections(
    date_from: str = None,
    date_to: str = None,
    num_people: int = None,
    session_id: str = None,
    track_id: str = None
):
    """البحث في السجلات"""
    try:
        results = system.db.search_detections(
            date_from=date_from,
            date_to=date_to,
            num_people=num_people,
            session_id=session_id,
            track_id=track_id
        )
        
        logger.info(f"🔍 Search completed: {len(results)} results")
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@app.post("/api/export")
async def export_results(session_ids: List[str]):
    """تصدير النتائج"""
    try:
        data = []
        for sid in session_ids:
            detections = system.db.get_recent_detections(sid, limit=1000)
            data.extend(detections)
        
        logger.info(f"📤 Export completed: {len(data)} records")
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ===== WebSocket للبث المباشر =====

class ConnectionManager:
    """مدير اتصالات WebSocket"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"❌ Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """إرسال رسالة لجميع العملاء"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # إزالة الاتصالات المفصولة
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@app.websocket("/ws/video")
async def websocket_video(websocket: WebSocket):
    """WebSocket للبث المباشر"""
    await manager.connect(websocket)
    
    try:
        while True:
            if system.is_running:
                # معالجة الإطار
                frame, stats = system.process_frame()
                
                if frame is not None:
                    # تحويل الإطار لـ base64
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    # إرسال البيانات
                    await websocket.send_json({
                        'type': 'frame',
                        'data': frame_base64,
                        'stats': stats
                    })
            
            await asyncio.sleep(0.033)  # ~30 FPS
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from video stream")

@app.websocket("/ws/stats")
async def websocket_stats(websocket: WebSocket):
    """WebSocket للإحصائيات فقط (أخف)"""
    await manager.connect(websocket)
    
    try:
        while True:
            if system.is_running:
                stats = {
                    'type': 'stats',
                    'people_count': system.people_count,
                    'faces_anonymized': system.faces_anonymized,
                    'frame_count': system.frame_count,
                    'track_ids': system.track_ids,
                    'timestamp': datetime.now().isoformat()
                }
                
                await websocket.send_json(stats)
            
            await asyncio.sleep(0.5)  # كل نصف ثانية
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ===== Startup & Shutdown =====

@app.on_event("startup")
async def startup_event():
    """عند تشغيل السيرفر"""
    logger.info("🚀 API Server started")
    logger.info(f"📍 Session ID: {system.session_id}")
    logger.info("🌐 WebSocket endpoints:")
    logger.info("   - ws://localhost:8000/ws/video (video stream)")
    logger.info("   - ws://localhost:8000/ws/stats (stats only)")

@app.on_event("shutdown")
async def shutdown_event():
    """عند إيقاف السيرفر"""
    system.stop()
    logger.info("🛑 API Server stopped")

# ===== تشغيل السيرفر =====

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════╗
    ║  Security Monitoring API Server        ║
    ║  ────────────────────────────────────  ║
    ║  🌐 API:       http://localhost:8000   ║
    ║  📡 WebSocket: ws://localhost:8000/ws  ║
    ║  📚 Docs:      /docs                    ║
    ║  🔍 Search:    /api/search              ║
    ╚══════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )