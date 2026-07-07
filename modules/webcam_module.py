# modules/webcam_module.py — Python
# modules/webcam_module.py
# Ambil satu frame dari webcam menggunakan OpenCV
# Menangani warm-up kamera dan error dengan graceful
 
import cv2
import logging
from datetime import datetime
import config
 
logger = logging.getLogger(__name__)
_cap = None
 
 
def init_camera():
    """Inisialisasi webcam sekali saat startup untuk mengurangi latency capture."""
    global _cap
    if _cap is not None and _cap.isOpened():
        return True
 
    _cap = cv2.VideoCapture(config.CAMERA_INDEX)
    if not _cap.isOpened():
        logger.error('[WEBCAM] Tidak dapat membuka kamera index=%d.', config.CAMERA_INDEX)
        _cap = None
        return False
 
    _cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    _cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    _cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
 
    # Warm-up singkat agar auto exposure dan exposure stabil
    for _ in range(5):
        _cap.read()
 
    logger.info('[WEBCAM] Kamera inisialisasi dan siap. index=%d', config.CAMERA_INDEX)
    return True
 
 
def capture_frame():
    """
    Ambil satu frame dari kamera yang sudah dibuka.
    """
    global _cap
    if _cap is None or not _cap.isOpened():
        if not init_camera():
            return None, None
 
    ret, frame = _cap.read()
    if not ret or frame is None:
        logger.warning('[WEBCAM] Gagal read frame, mencoba ulang...')
        # Coba sekali lagi jika frame pertama gagal
        ret, frame = _cap.read()
 
    if not ret or frame is None:
        logger.error('[WEBCAM] Gagal mengambil frame dari kamera index=%d.', config.CAMERA_INDEX)
        return None, None
 
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = config.CAPTURES_DIR / f'raw_{ts}.jpg'
    cv2.imwrite(str(filepath), frame)
    logger.info('[WEBCAM] Frame disimpan: %s', filepath)
    return frame, str(filepath)
 
 
def close_camera():
    """Tutup kamera saat sistem shutdown."""
    global _cap
    if _cap is not None:
        if _cap.isOpened():
            _cap.release()
            logger.info('[WEBCAM] Kamera ditutup.')
        _cap = None
