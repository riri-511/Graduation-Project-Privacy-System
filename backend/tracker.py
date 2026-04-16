import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import  DeepSort
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonTracker:
    """متتبع الأشخاص باستخدام DeepSORT"""
    
    def __init__(self, max_age: int = 30, n_init: int = 3):
        """
        تهيئة المتتبع
        
        Args:
            max_age: عدد الإطارات قبل حذف المسار
            n_init: عدد الكشوفات المتتالية لتأكيد المسار
        """
        try:
            self.tracker = DeepSort(
                max_age=max_age,
                n_init=n_init,
                nms_max_overlap=1.0,
                max_cosine_distance=0.3,
                nn_budget=None,
                embedder="mobilenet",
                half=True,
                embedder_gpu=True
            )
            self.track_history = {}
            self.colors = {}
            logger.info("✅ تم تهيئة نظام التتبع DeepSORT")
        except Exception as e:
            logger.error(f"❌ خطأ في تهيئة التتبع: {e}")
            raise
    
    def update(self, detections: List, frame: np.ndarray) -> Tuple[List, np.ndarray]:
        """
        تحديث التتبع بالكشوفات الجديدة
        
        Args:
            detections: قائمة الكشوفات من الـ detector
            frame: الإطار الحالي
            
        Returns:
            tuple: (المسارات المحدثة, الإطار مع التتبع)
        """
        # تحويل الكشوفات لصيغة DeepSORT
        deepsort_detections = []
        for det in detections:
            bbox = det['bbox']
            conf = det['confidence']
            # تحويل من [x1,y1,x2,y2] إلى [x,y,w,h]
            x, y, w, h = bbox[0], bbox[1], bbox[2]-bbox[0], bbox[3]-bbox[1]
            deepsort_detections.append(([x, y, w, h], conf, 'person'))
        
        # تحديث التتبع
        tracks = self.tracker.update_tracks(deepsort_detections, frame=frame)
        
        # معالجة المسارات
        active_tracks = []
        annotated_frame = frame.copy()
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            bbox = track.to_ltrb()  # [left, top, right, bottom]
            
            # توليد لون ثابت لكل ID
            if track_id not in self.colors:
                self.colors[track_id] = tuple(np.random.randint(0, 255, 3).tolist())
            
            color = self.colors[track_id]
            
            # رسم المربع
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
            
            # إضافة ID
            label = f"ID: {track_id}"
            cv2.putText(annotated_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # حفظ تاريخ المسار
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            if track_id not in self.track_history:
                self.track_history[track_id] = []
            self.track_history[track_id].append(center)
            
            # رسم المسار
            if len(self.track_history[track_id]) > 1:
                points = np.array(self.track_history[track_id], dtype=np.int32)
                cv2.polylines(annotated_frame, [points], False, color, 2)
            
            # حفظ معلومات المسار
            track_info = {
                'id': track_id,
                'bbox': [x1, y1, x2, y2],
                'center': center,
                'color': color
            }
            active_tracks.append(track_info)
        
        return active_tracks, annotated_frame
    
    def get_active_ids(self) -> List[int]:
        """الحصول على IDs النشطة"""
        return list(self.colors.keys())
    
    def reset(self):
        """إعادة تعيين التتبع"""
        self.track_history.clear()
        self.colors.clear()
        logger.info("🔄 تم إعادة تعيين التتبع")


# مثال للاستخدام المتكامل
if __name__ == "__main__":
    from detector import PersonDetector
    
    # تهيئة الكاشف والمتتبع
    detector = PersonDetector(model_path='yolov8n.pt', conf_threshold=0.5)
    tracker = PersonTracker(max_age=30, n_init=3)
    
    # فتح الكاميرا
    cap = cv2.VideoCapture(0)
    
    print("🎥 بدء الكشف والتتبع... اضغط 'q' للخروج")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # الكشف
        detections, _ = detector.detect(frame)
        
        # التتبع
        tracks, annotated_frame = tracker.update(detections, frame)
        
        # عرض المعلومات
        info_text = f"Frame: {frame_count} | People: {len(tracks)} | IDs: {len(tracker.get_active_ids())}"
        cv2.putText(annotated_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # عرض النتيجة
        cv2.imshow('Person Detection & Tracking', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()