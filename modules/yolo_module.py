# modules/yolo_module.py — Python
# modules/yolo_module.py
# Jalankan YOLOv8 untuk mendeteksi orang dalam frame
# Menghasilkan foto ter-anotasi dengan bounding box
 
import cv2
import logging
from datetime import datetime
import config
 
logger  = logging.getLogger(__name__)
_model  = None  # Model disimpan di memori setelah load pertama kali
 
 
def init_yolo():
    """
    Load model YOLOv8 ke memori.
    Panggil SEKALI saat startup — memakan waktu 5–30 detik pertama kali.
    Model akan otomatis di-download (~6MB) jika belum ada.
    """
    global _model
    logger.info('[YOLO] Memuat model: %s ...', config.YOLO_MODEL)
    try:
        from ultralytics import YOLO
        _model = YOLO(config.YOLO_MODEL)
        logger.info('[YOLO] Model berhasil dimuat.')
    except Exception as e:
        logger.error('[YOLO] Gagal memuat model: %s', e)
        raise  # Re-raise karena tanpa model AI tidak bisa berjalan
 
 
def detect(frame):
    """
    Jalankan deteksi objek pada frame dari webcam.
 
    Args:
        frame: numpy array dari cv2.VideoCapture.read()
 
    Returns:
        tuple: (annotated_frame, num_persons, saved_path)
               annotated_frame: frame dengan bounding box digambar
               num_persons: jumlah orang yang terdeteksi
               saved_path: path file foto ter-anotasi yang disimpan
    """
    if _model is None:
        logger.error('[YOLO] Model belum diload. Panggil init_yolo() dulu.')
        return frame, 0, None
 
    # Jalankan inferensi — hanya deteksi class 0 (person)
    results = _model(
        frame,
        classes  = [0],                  # 0 = person (manusia)
        conf     = config.YOLO_CONF,     # Threshold confidence
        imgsz    = config.YOLO_IMG_SIZE, # Ukuran gambar input
        verbose  = False,                # Jangan print ke stdout
    )
 
    # Gambar bounding box di atas frame
    annotated = results[0].plot()
 
    # Hitung jumlah orang terdeteksi
    boxes       = results[0].boxes
    num_persons = len(boxes) if boxes is not None else 0
 
    # Tambahkan overlay informasi di sudut kiri atas foto
    ts       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    freq_mhz = config.SDR_FREQUENCY / 1e6
    overlay  = f'SIGINT CAPTURE | {freq_mhz:.3f} MHz | {ts}'
    cv2.putText(
        annotated, overlay,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 165, 255),  # Warna orange (BGR format OpenCV)
        2,              # Ketebalan teks
    )
 
    # Simpan foto ter-anotasi
    ts2      = datetime.now().strftime('%Y%m%d_%H%M%S')
    savepath = config.CAPTURES_DIR / f'yolo_{ts2}.jpg'
    cv2.imwrite(str(savepath), annotated)
 
    logger.info(
        '[YOLO] %d orang terdeteksi. Foto disimpan: %s',
        num_persons, savepath
    )
    return annotated, num_persons, str(savepath)
