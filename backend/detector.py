import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonDetector:
    """كاشف الأشخاص باستخدام YOLO"""
    
    def __init__(self, model_path: str = 'yolov8n.pt', conf_threshold: float = 0.5):
        """
        تهيئة كاشف الأشخاص
        
        Args:
            model_path: مسار نموذج YOLO
            conf_threshold: حد الثقة للكشف
        """
        try:
            self.model = YOLO(model_path)
            self.conf_threshold = conf_threshold
            self.class_names = self.model.names
            logger.info(f"✅ تم تحميل نموذج YOLO من {model_path}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحميل النموذج: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> Tuple[List, np.ndarray]:
        """
        كشف الأشخاص في الإطار
        
        Args:
            frame: الإطار المراد فحصه
            
        Returns:
            tuple: (قائمة الكشوفات, الإطار المعالج)
        """
        results = self.model(frame, conf=self.conf_threshold, classes=[0], verbose=False)
        
        detections = []
        annotated_frame = frame.copy()
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # استخراج الإحداثيات
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # حفظ بيانات الكشف
                detection = {
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class': cls,
                    'class_name': self.class_names[cls]
                }
                detections.append(detection)
                
                # رسم المربع
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # إضافة النص
                label = f"{self.class_names[cls]}: {conf:.2f}"
                cv2.putText(annotated_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return detections, annotated_frame
    
    def get_person_count(self, detections: List) -> int:
        """عد الأشخاص المكتشفين"""
        return len(detections)
    
    def filter_by_confidence(self, detections: List, min_conf: float = 0.5) -> List:
        """تصفية الكشوفات حسب الثقة"""
        return [d for d in detections if d['confidence'] >= min_conf]


# مثال للاستخدام
if __name__ == "__main__":
    # تهيئة الكاشف
    detector = PersonDetector(model_path='yolov8n.pt', conf_threshold=0.5)
    
    # فتح الكاميرا أو فيديو
    cap = cv2.VideoCapture(0)  # 0 للكاميرا أو ضع مسار الفيديو
    
    print("🎥 بدء الكشف... اضغط 'q' للخروج")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # كشف الأشخاص
        detections, annotated_frame = detector.detect(frame)
        
        # عرض عدد الأشخاص
        count = detector.get_person_count(detections)
        cv2.putText(annotated_frame, f"People: {count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # عرض النتيجة
        cv2.imshow('Person Detection', annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()