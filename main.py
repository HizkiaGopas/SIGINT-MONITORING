# main.py — Python
# main.py — Pusat Kendali Sistem Hibrida
# Jalankan dengan: python main.py

import time
import logging
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
 
import config
from modules import (
    webcam_module,
    yolo_module,
    alarm_module,
    telegram_module,
    db_module,
    flask_server,
    manual_trigger_module,
)
 
 
# ─────────────────────────────────────────────────────────
# SETUP LOGGING
# ─────────────────────────────────────────────────────────
 
def setup_logging():
    """
    Konfigurasi sistem logging.
    Log ditulis ke dua tempat sekaligus:
    1. File logs/system.log (dengan rotasi otomatis)
    2. Terminal (stdout) agar operator bisa memantau langsung
    """
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    file_handler = RotatingFileHandler(
        str(config.LOG_PATH),
        maxBytes    = config.LOG_MAX_BYTES,
        backupCount = config.LOG_BACKUP_COUNT,
        encoding    = 'utf-8',
    )
    file_handler.setFormatter(formatter)
 
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
 
    logging.basicConfig(
        level    = logging.INFO,
        handlers = [file_handler, console_handler],
    )
 
 
# ─────────────────────────────────────────────────────────
# INISIALISASI SEMUA MODUL
# ─────────────────────────────────────────────────────────
 
def initialize():
    """
    Inisialisasi semua modul dalam urutan yang benar.
    Database harus pertama, lalu AI, lalu server, lalu trigger.
    """
    logging.info('=' * 55)
    logging.info('  SIGINT STATION v4.0 HYBRID — BOOT SEQUENCE')
    logging.info('=' * 55)
 
    # 1. Database — harus pertama agar modul lain bisa simpan data
    db_module.init_db()
    logging.info('[BOOT] Database OK.')
 
    # 2. Inisialisasi kamera sekali untuk mempercepat capture manual
    logging.info('[BOOT] Inisialisasi kamera...')
    webcam_module.init_camera()
    logging.info('[BOOT] Kamera OK.')
 
    # 3. Load model YOLOv8 — memakan waktu 5-30 detik
    logging.info('[BOOT] Memuat model YOLOv8 (harap tunggu)...')
    yolo_module.init_yolo()
    logging.info('[BOOT] YOLOv8 OK.')
 
    # 3. Inisialisasi alarm (serial Arduino + audio)
    alarm_module.init_alarm()
    logging.info('[BOOT] Alarm module OK.')
 
    # 4. Jalankan Flask server di background
    flask_server.start_server()
    logging.info('[BOOT] Flask server OK.')
 
    # 5. Inisialisasi input trigger
    if config.MANUAL_TRIGGER_MODE:
        manual_trigger_module.init_manual_trigger()
        logging.info('[BOOT] Manual Trigger Mode AKTIF — Tombol: [%s].',
                     config.MANUAL_TRIGGER_KEY.upper())
    else:
        # Mode RTL-SDR — import hanya saat dibutuhkan
        from modules import sdr_module
        sdr_module.init_sdr()
        logging.info('[BOOT] RTL-SDR Mode AKTIF.')
 
    logging.info('[BOOT] Semua modul berhasil diinisialisasi.')
    logging.info('[BOOT] Dashboard tersedia di: http://[IP-RPi5]:%d', config.FLASK_PORT)
 
 
# ─────────────────────────────────────────────────────────
# PIPELINE DETEKSI — Dipanggil setiap ada trigger
# ─────────────────────────────────────────────────────────
 
def handle_detection(power_db: float = -35.0):
    """
    Eksekusi seluruh pipeline setelah trigger diterima.
    Urutan: Webcam → YOLOv8 → SQLite → Alarm → Telegram → Dashboard.
 
    Args:
        power_db: Kekuatan sinyal dalam dBm.
                  -35.0 adalah nilai simulasi untuk Mode Demo.
    """
    freq_mhz = config.SDR_FREQUENCY / 1e6
    mode_tag = '[DEMO]' if config.MANUAL_TRIGGER_MODE else '[SDR]'
    logging.info('%s Pipeline deteksi dimulai: %.1f dBm @ %.3f MHz.',
                 mode_tag, power_db, freq_mhz)
 
    # ① Ambil foto dari webcam
    frame, raw_path = webcam_module.capture_frame()
    image_path = raw_path  # Default ke foto mentah
 
    # ② Jalankan AI detection jika foto berhasil diambil
    persons = 0
    if frame is not None:
        _, persons, yolo_path = yolo_module.detect(frame)
        if yolo_path:
            image_path = yolo_path  # Gunakan foto ter-anotasi
 
    # ③ Simpan event ke database SQLite
    event_id = db_module.save_event(
        frequency  = freq_mhz,
        power_db   = power_db,
        persons    = persons,
        image_path = image_path,
    )
 
    # ④ Nyalakan alarm fisik (Arduino) dan suara — non-blocking
    alarm_module.play()
 
    # ⑤ Kirim laporan ke Telegram — non-blocking
    telegram_module.send_report(
        image_path = image_path,
        power_db   = power_db,
        freq_mhz   = freq_mhz,
        persons    = persons,
        event_id   = event_id,
    )
 
    # ⑥ Push update ke dashboard via WebSocket (Cross-Platform Ready)
    import os
    nama_file_foto = os.path.basename(image_path) if image_path else None
    
    payload_dashboard = {
        "event_id": event_id,
        "time": time.strftime("%H:%M:%S"),
        "date": time.strftime("%Y-%m-%d"),
        "freq": freq_mhz,
        "power": power_db,
        "persons": persons,
        # Kirim path relatif untuk diproses dashboard
        "image": f"/captures/{nama_file_foto}" if nama_file_foto else None,
    }
    flask_server.emit_event(payload_dashboard)
 
    logging.info('%s Pipeline selesai — Event #%d | %d orang.',
                 mode_tag, event_id, persons)
 
 
# ─────────────────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────────────────
 
def main():
    """Entry point utama — setup logging, inisialisasi, lalu masuk loop."""
    setup_logging()
    initialize()
 
    last_trigger_time = 0  # Waktu trigger terakhir (untuk cooldown)
    logging.info('[MAIN] Memasuki monitoring loop. Tekan Ctrl+C untuk berhenti.')
 
    try:
        print("[MAIN] Memasuki monitoring loop. Tekan Ctrl+C untuk berhenti.")
        while True:
            if config.MANUAL_TRIGGER_MODE:
                # ── MODE DEMO (MANUAL TRIGGER) ──────────────
                # wait_for_trigger() MEMBLOKIR di sini sampai SPASI ditekan.
                # CPU usage = ~0% saat menunggu (event-driven, sangat efisien).
                triggered = manual_trigger_module.wait_for_trigger()
 
                if triggered:
                    now = time.time()
                    if now - last_trigger_time >= config.COOLDOWN_SEC:
                        last_trigger_time = now
                        handle_detection(power_db=-35.0)  # Nilai simulasi
                    else:
                        remaining = config.COOLDOWN_SEC - (now - last_trigger_time)
                        logging.info(
                            '[MAIN] Trigger diabaikan: cooldown %.1f detik lagi.',
                            remaining
                        )
 
            else:
                # ── MODE NORMAL (RTL-SDR) ───────────────────
                from modules import sdr_module
                power_db = sdr_module.read_power_db()
 
                if sdr_module.is_signal_detected(power_db):
                    now = time.time()
                    if now - last_trigger_time >= config.COOLDOWN_SEC:
                        last_trigger_time = now
                        handle_detection(power_db=power_db)
 
                
                time.sleep(0.05)  # 50ms polling interval
 
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Menerima sinyal Ctrl+C. Menghentikan Stasiun Taktis...")
      
 
    finally:
        # Cleanup sumber daya saat shutdown
        if config.MANUAL_TRIGGER_MODE:
            manual_trigger_module.stop_manual_trigger()
        webcam_module.close_camera()
        alarm_module.close_serial()
        logging.info('[MAIN] === SIGINT STATION BERHENTI ===')
 
 
# ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    main()
