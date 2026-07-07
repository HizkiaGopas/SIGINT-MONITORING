# config.py — Python
# config.py — Pusat Pengaturan Sistem
# JANGAN ubah file ini kecuali untuk menyesuaikan hardware
 
import os
from dotenv import load_dotenv
from pathlib import Path
 
# Muat variabel dari file .env
load_dotenv()
 
# ─────────────────────────────────────────────────────────
# DIREKTORI SISTEM
# ─────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent           # ~/sigint-station/
DATA_DIR     = BASE_DIR / 'data'               # ~/sigint-station/data/
CAPTURES_DIR = DATA_DIR / 'captures'           # Tempat simpan foto
LOGS_DIR     = BASE_DIR / 'logs'               # Tempat simpan log
SOUNDS_DIR   = BASE_DIR / 'sounds'             # File suara alarm
DB_PATH      = DATA_DIR / 'sigint.db'          # Database SQLite
LOG_PATH     = LOGS_DIR / 'system.log'         # File log utama
ALARM_FILE   = SOUNDS_DIR / 'alert.wav'        # File suara alarm
 
# Buat semua direktori otomatis jika belum ada
for d in [DATA_DIR, CAPTURES_DIR, LOGS_DIR, SOUNDS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
 
# ─────────────────────────────────────────────────────────
# MODE OPERASI
# ─────────────────────────────────────────────────────────
# True  = Mode Demo: tombol SPASI sebagai trigger (tanpa RTL-SDR)
# False = Mode Normal: RTL-SDR sebagai trigger (jika hardware tersedia)
MANUAL_TRIGGER_MODE = os.getenv('MANUAL_TRIGGER_MODE', 'True').lower() == 'true'
 
# Tombol keyboard untuk trigger manual
# Nilai valid: 'space', 'enter', 'f1' s/d 'f12'
MANUAL_TRIGGER_KEY  = os.getenv('MANUAL_TRIGGER_KEY', 'space')
 
# Pesan yang tampil di terminal saat menunggu trigger
MANUAL_TRIGGER_MSG  = ('[MODE DEMO] Sistem aktif dan siap.'
                       ' Tekan SPASI untuk memicu deteksi.')
 
# ─────────────────────────────────────────────────────────
# ARDUINO SERIAL
# ─────────────────────────────────────────────────────────
# Apakah alarm fisik Arduino diaktifkan?
ARDUINO_ENABLED = os.getenv('ARDUINO_ENABLED', 'True').lower() == 'true'
 
# Port serial Arduino di Raspberry Pi:
# /dev/ttyACM0 → Arduino Uno via USB (paling umum)
# /dev/ttyUSB0 → Arduino dengan chip CH340 (beberapa klon)
ARDUINO_PORT    = os.getenv('ARDUINO_PORT', '/dev/ttyACM0')
 
# Kecepatan komunikasi serial — HARUS sama dengan sketch Arduino
ARDUINO_BAUD    = int(os.getenv('ARDUINO_BAUD', '9600'))
 
# Timeout membaca serial (detik)
ARDUINO_TIMEOUT = float(os.getenv('ARDUINO_TIMEOUT', '1.0'))
 
# Karakter yang dikirim ke Arduino sebagai sinyal trigger
ARDUINO_SIGNAL  = os.getenv('ARDUINO_SIGNAL', 'A')
 
# ─────────────────────────────────────────────────────────
# KAMERA DAN AI
# ─────────────────────────────────────────────────────────
# Index webcam: 0 = webcam pertama, 1 = webcam kedua, dst.
CAMERA_INDEX   = int(os.getenv('CAMERA_INDEX', '0'))
 
# Model YOLOv8: 'yolov8n.pt' = nano (tercepat, direkomendasikan untuk RPi5)
YOLO_MODEL     = os.getenv('YOLO_MODEL', 'yolov8n.pt')
 
# Confidence threshold: 0.0 – 1.0 (lebih tinggi = lebih selektif)
YOLO_CONF      = float(os.getenv('YOLO_CONF', '0.40'))
 
# Ukuran gambar input AI: 320 = cepat, 416 = lebih akurat
YOLO_IMG_SIZE  = int(os.getenv('YOLO_IMG_SIZE', '320'))
 
# ─────────────────────────────────────────────────────────
# SISTEM DAN JARINGAN
# ─────────────────────────────────────────────────────────
# Jarak waktu minimum antar dua trigger (detik) — cegah spam
COOLDOWN_SEC   = int(os.getenv('COOLDOWN_SEC', '5'))
 
# Frekuensi simulasi (digunakan untuk label di database dan Telegram)
SDR_FREQUENCY  = float(os.getenv('SDR_FREQUENCY', '145000000'))  # Hz
 
# Host dan port Flask server (dashboard dan API)
FLASK_HOST     = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT     = int(os.getenv('FLASK_PORT', '5000'))
 
# ─────────────────────────────────────────────────────────
# TELEGRAM BOT
# ─────────────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
 
# ─────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────
# Maksimal ukuran file log sebelum dirotasi (5MB)
LOG_MAX_BYTES    = 5 * 1024 * 1024
 
# Berapa file log lama yang disimpan sebelum dihapus
LOG_BACKUP_COUNT = 3
