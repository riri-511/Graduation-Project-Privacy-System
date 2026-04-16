import cv2
import numpy as np
import mediapipe as mp
from typing import List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceAnonymizer:
    """نظام إخفاء الوجوه"""
    
    def __init__(self, method: str = 'blur', blur_intensity: int = 51):
        """
        تهيئة نظام الإخفاء
        
        Args:
            method: طريقة الإخفاء (blur, pixelate, blackbox)
            blur_intensity: شدة الطمس (يجب أن تكون رقم فردي)
        """
        self.method = method
        self.blur_intensity = blur_intensity if blur_intensity % 2 == 1 else blur_intensity + 1
        
        # تهيئة MediaPipe للكشف عن الوجوه
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 0 للقريب، 1 للبعيد
            min_detection_confidence=0.5
        )
        
        logger.info(f"✅ تم تهيئة نظام الإخفاء بطريقة: {method}")
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        كشف الوجوه في الإطار
        
        Args:
            frame: الإطار المراد فحصه
            
        Returns:
            قائمة بإحداثيات الوجوه [x, y, w, h]
        """
        # تحويل لـ RGB (MediaPipe يستخدم RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(rgb_frame)
        
        faces = []
        if results.detections:
            h, w, _ = frame.shape
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # التأكد من الإحداثيات داخل الإطار
                x = max(0, x)
                y = max(0, y)
                width = min(width, w - x)
                height = min(height, h - y)
                
                faces.append((x, y, width, height))
        
        return faces
    
    def blur_face(self, frame: np.ndarray, face: Tuple[int, int, int, int]) -> np.ndarray:
        """طمس الوجه"""
        x, y, w, h = face
        face_region = frame[y:y+h, x:x+w]
        
        if face_region.size > 0:
            blurred = cv2.GaussianBlur(face_region, (self.blur_intensity, self.blur_intensity), 0)
            frame[y:y+h, x:x+w] = blurred
        
        return frame
    
    def pixelate_face(self, frame: np.ndarray, face: Tuple[int, int, int, int], 
                      pixel_size: int = 15) -> np.ndarray:
        """تنقيط الوجه"""
        x, y, w, h = face
        face_region = frame[y:y+h, x:x+w]
        
        if face_region.size > 0 and w > 0 and h > 0:
            # تصغير ثم تكبير لعمل تأثير التنقيط
            temp = cv2.resize(face_region, (pixel_size, pixel_size), interpolation=cv2.INTER_LINEAR)
            pixelated = cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)
            frame[y:y+h, x:x+w] = pixelated
        
        return frame
    
    def blackbox_face(self, frame: np.ndarray, face: Tuple[int, int, int, int]) -> np.ndarray:
        """صندوق أسود على الوجه"""
        x, y, w, h = face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 0), -1)
        return frame
    
    def anonymize(self, frame: np.ndarray, person_bboxes: List = None) -> Tuple[np.ndarray, int]:
        """
        إخفاء الوجوه في الإطار
        
        Args:
            frame: الإطار المراد معالجته
            person_bboxes: مربعات الأشخاص المكتشفين (اختياري للتحسين)
            
        Returns:
            tuple: (الإطار المعالج, عدد الوجوه المخفية)
        """
        anonymized_frame = frame.copy()
        
        # كشف الوجوه
        faces = self.detect_faces(frame)
        
        # تطبيق الإخفاء
        for face in faces:
            if self.method == 'blur':
                anonymized_frame = self.blur_face(anonymized_frame, face)
            elif self.method == 'pixelate':
                anonymized_frame = self.pixelate_face(anonymized_frame, face)
            elif self.method == 'blackbox':
                anonymized_frame = self.blackbox_face(anonymized_frame, face)
        
        return anonymized_frame, len(faces)
    
    def annotate_faces(self, frame: np.ndarray) -> np.ndarray:
        """رسم مربعات حول الوجوه (للتجربة فقط)"""
        faces = self.detect_faces(frame)
        annotated = frame.copy()
        
        for x, y, w, h in faces:
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(annotated, "Face", (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        return annotated
    
    def __del__(self):
        """تنظيف الموارد"""
        self.face_detection.close()


# مثال للاستخدام الكامل
if __name__ == "__main__":
    from detector import PersonDetector
    from tracker import PersonTracker
    
    # تهيئة جميع المكونات
    detector = PersonDetector(model_path='yolov8n.pt', conf_threshold=0.5)
    tracker = PersonTracker(max_age=30, n_init=3)
    anonymizer = FaceAnonymizer(method='blur', blur_intensity=51)
    
    # فتح الكاميرا
    cap = cv2.VideoCapture(0)
    
    print("🎥 النظام الكامل: كشف + تتبع + إخفاء الهوية")
    print("اضغط: 'q' للخروج | '1' blur | '2' pixelate | '3' blackbox")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 1. الكشف
        detections, _ = detector.detect(frame)
        
        # 2. التتبع
        tracks, tracked_frame = tracker.update(detections, frame)
        
        # 3. إخفاء الوجوه
        anonymized_frame, face_count = anonymizer.anonymize(tracked_frame)
        
        # عرض المعلومات
        info = f"People: {len(tracks)} | Faces Anonymized: {face_count} | Method: {anonymizer.method}"
        cv2.putText(anonymized_frame, info, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # عرض النتيجة
        cv2.imshow('Complete System', anonymized_frame)
        
        # التحكم
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('1'):
            anonymizer.method = 'blur'
            print("✅ تم التغيير إلى: Blur")
        elif key == ord('2'):
            anonymizer.method = 'pixelate'
            print("✅ تم التغيير إلى: Pixelate")
        elif key == ord('3'):
            anonymizer.method = 'blackbox'
            print("✅ تم التغيير إلى: Blackbox")
    
    cap.release()
    cv2.destroyAllWindows()