# modules/webcam_module.py — Python
# modules/webcam_module.py
# Ambil satu frame dari webcam menggunakan OpenCV
# Menangani warm-up kamera dan error dengan graceful
 
import cv2
import logging
from datetime import datetime
import config
 
logger = logging.getLogger(__name__)
 
 
def capture_frame():
    """
    Buka webcam, ambil satu frame, simpan ke file, tutup webcam.
 
    Mengapa dibuka dan ditutup setiap kali?
    Karena RPi5 perlu memori untuk proses AI — tidak perlu streaming terus-menerus.
 
    Returns:
        tuple: (frame_ndarray, filepath_string) jika berhasil.
               (None, None) jika gagal.
    """
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
 
    # Set resolusi kamera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
 
    # Warm-up: baca beberapa frame dulu agar auto-exposure stabil
    # Tanpa ini, foto sering terlalu gelap atau terlalu terang
    for _ in range(10):
        cap.read()
 
    # Ambil frame yang sebenarnya
    ret, frame = cap.read()
    cap.release()  # Tutup kamera segera setelah ambil frame
 
    if not ret or frame is None:
        logger.error(
            '[WEBCAM] Gagal mengambil frame dari kamera index=%d.',
            config.CAMERA_INDEX
        )
        return None, None
 
    # Generate nama file dengan timestamp
    ts       = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = config.CAPTURES_DIR / f'raw_{ts}.jpg'
 
    # Simpan frame mentah (sebelum diproses YOLOv8)
    cv2.imwrite(str(filepath), frame)
    logger.info('[WEBCAM] Frame disimpan: %s', filepath)
 
    return frame, str(filepath)
