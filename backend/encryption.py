
import os
import cv2
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pickle
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoEncryptor:
    """نظام تشفير الفيديو"""
    
    def __init__(self, key_storage_path: str = 'data/keys'):
        """
        تهيئة نظام التشفير
        
        Args:
            key_storage_path: مسار تخزين المفاتيح
        """
        self.key_storage_path = Path(key_storage_path)
        self.key_storage_path.mkdir(parents=True, exist_ok=True)
        
        # توليد أو تحميل المفتاح الرئيسي
        self.master_key_path = self.key_storage_path / 'master.key'
        self.master_key = self._load_or_generate_master_key()
        
        logger.info("✅ تم تهيئة نظام التشفير AES-256")
    
    def _load_or_generate_master_key(self) -> bytes:
        """تحميل أو توليد المفتاح الرئيسي"""
        if self.master_key_path.exists():
            with open(self.master_key_path, 'rb') as f:
                key = f.read()
            logger.info("🔑 تم تحميل المفتاح الرئيسي")
        else:
            key = os.urandom(32)  # 256 bit
            with open(self.master_key_path, 'wb') as f:
                f.write(key)
            logger.info("🔑 تم توليد مفتاح رئيسي جديد")
        return key
    
    def generate_session_key(self, session_id: str) -> bytes:
        """
        توليد مفتاح جلسة من المفتاح الرئيسي
        
        Args:
            session_id: معرف الجلسة
            
        Returns:
            مفتاح الجلسة
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
)

        
        return kdf.derive(self.master_key)
    
    def encrypt_frame(self, frame: np.ndarray, key: bytes) -> bytes:
        """
        تشفير إطار واحد
        
        Args:
            frame: الإطار المراد تشفيره
            key: مفتاح التشفير
            
        Returns:
            البيانات المشفرة
        """
        # تحويل الإطار لـ bytes
        frame_bytes = pickle.dumps(frame)
        
        # توليد IV عشوائي
        iv = os.urandom(16)
        
        # التشفير
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Padding
        padding_length = 16 - (len(frame_bytes) % 16)
        padded_data = frame_bytes + bytes([padding_length] * padding_length)
        
        # تشفير
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # دمج IV مع البيانات المشفرة
        return iv + encrypted_data
    
    def decrypt_frame(self, encrypted_data: bytes, key: bytes) -> np.ndarray:
        """
        فك تشفير إطار
        
        Args:
            encrypted_data: البيانات المشفرة
            key: مفتاح فك التشفير
            
        Returns:
            الإطار الأصلي
        """
        # فصل IV
        iv = encrypted_data[:16]
        encrypted_frame = encrypted_data[16:]
        
        # فك التشفير
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(encrypted_frame) + decryptor.finalize()
        
        # إزالة الـ Padding
        padding_length = padded_data[-1]
        frame_bytes = padded_data[:-padding_length]
        
        # تحويل لإطار
        frame = pickle.loads(frame_bytes)
        return frame
    
    def encrypt_video_stream(self, frames: list, session_id: str, output_path: str) -> dict:
        """
        تشفير مجموعة إطارات وحفظها
        
        Args:
            frames: قائمة الإطارات
            session_id: معرف الجلسة
            output_path: مسار حفظ الفيديو المشفر
            
        Returns:
            معلومات الجلسة
        """
        # توليد مفتاح الجلسة
        session_key = self.generate_session_key(session_id)
        
        # تشفير الإطارات
        encrypted_frames = []
        for i, frame in enumerate(frames):
            encrypted_frame = self.encrypt_frame(frame, session_key)
            encrypted_frames.append(encrypted_frame)
            
            if (i + 1) % 30 == 0:
                logger.info(f"🔒 تم تشفير {i + 1}/{len(frames)} إطار")
        
        # حفظ البيانات المشفرة
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            pickle.dump(encrypted_frames, f)
        
        # حفظ معلومات الجلسة
        metadata = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'frame_count': len(frames),
            'encrypted_file': str(output_path),
            'encryption_algorithm': 'AES-256-CBC'
        }
        
        metadata_path = output_path.with_suffix('.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ تم تشفير وحفظ {len(frames)} إطار في {output_path}")
        
        return metadata
    
    def decrypt_video_stream(self, encrypted_path: str, session_id: str) -> list:
        """
        فك تشفير فيديو محفوظ
        
        Args:
            encrypted_path: مسار الفيديو المشفر
            session_id: معرف الجلسة
            
        Returns:
            قائمة الإطارات الأصلية
        """
        # توليد مفتاح الجلسة
        session_key = self.generate_session_key(session_id)
        
        # تحميل البيانات المشفرة
        with open(encrypted_path, 'rb') as f:
            encrypted_frames = pickle.load(f)
        
        # فك التشفير
        frames = []
        for i, encrypted_frame in enumerate(encrypted_frames):
            frame = self.decrypt_frame(encrypted_frame, session_key)
            frames.append(frame)
            
            if (i + 1) % 30 == 0:
                logger.info(f"🔓 تم فك تشفير {i + 1}/{len(encrypted_frames)} إطار")
        
        logger.info(f"✅ تم فك تشفير {len(frames)} إطار")
        
        return frames
    
    def save_encrypted_video(self, cap_source, duration_sec: int, session_id: str, 
                            output_dir: str = 'data/encrypted') -> dict:
        """
        تسجيل وتشفير فيديو مباشر
        
        Args:
            cap_source: مصدر الفيديو (كاميرا أو ملف)
            duration_sec: مدة التسجيل بالثواني
            session_id: معرف الجلسة
            output_dir: مجلد الحفظ
            
        Returns:
            معلومات الجلسة
        """
        cap = cv2.VideoCapture(cap_source)
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        total_frames = fps * duration_sec
        
        frames = []
        logger.info(f"📹 بدء التسجيل لمدة {duration_sec} ثانية...")
        
        for i in range(total_frames):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            
            if (i + 1) % fps == 0:
                logger.info(f"⏱️ تم تسجيل {(i + 1) // fps} ثانية")
        
        cap.release()
        
        # تشفير وحفظ
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{output_dir}/encrypted_{session_id}_{timestamp}.enc"
        
        metadata = self.encrypt_video_stream(frames, session_id, output_path)
        
        return metadata


# مثال للاستخدام
if __name__ == "__main__":
    # تهيئة التشفير
    encryptor = VideoEncryptor(key_storage_path='data/keys')
    
    # مثال 1: تشفير إطارات
    print("\n=== مثال 1: تشفير إطارات ===")
    cap = cv2.VideoCapture(0)
    frames = []
    
    print("📹 جمع 90 إطار (3 ثواني)...")
    for _ in range(90):
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    
    session_id = "test_session_001"
    metadata = encryptor.encrypt_video_stream(
        frames, 
        session_id, 
        'data/encrypted/test_video.enc'
    )
    
    print(f"\n✅ تم التشفير بنجاح!")
    print(f"📁 الملف: {metadata['encrypted_file']}")
    print(f"🔢 عدد الإطارات: {metadata['frame_count']}")
    
    # مثال 2: فك التشفير
    print("\n=== مثال 2: فك التشفير ===")
    decrypted_frames = encryptor.decrypt_video_stream(
        'data/encrypted/test_video.enc',
        session_id
    )
    
    print(f"✅ تم فك التشفير: {len(decrypted_frames)} إطار")
    
    # عرض بعض الإطارات
    print("\n👁️ اضغط أي زر للإطار التالي، 'q' للخروج")
    for i, frame in enumerate(decrypted_frames[::30]):  # كل 30 إطار
        cv2.imshow(f'Decrypted Frame {i}', frame)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()
    print("\n✅ انتهى الاختبار!")