# modules/telegram_module.py
import os
import logging
import threading
import requests
import config

logger = logging.getLogger(__name__)

def _execute_send(image_path, power_db, freq_mhz, persons, event_id):
    """Fungsi murni sinkron yang berjalan di latar belakang (Instan)"""
    token = config.TELEGRAM_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    
    caption_text = (
        f"🚨 DETEKSI SISTEM SIGINT\n\n"
        f"Event ID: #{event_id}\n"
        f"Frekuensi: {freq_mhz} MHz\n"
        f"Power: {power_db} dBm\n"
        f"Jumlah Orang: {persons}\n"
        f"Status: Peringatan Otomatis"
    )
    
    try:
        # Menembak langsung secara paralel tanpa memblokir RPi5/Laptop
        if image_path and os.path.exists(image_path):
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            payload = {"chat_id": chat_id, "caption": caption_text}
            with open(image_path, "rb") as foto:
                files = {"photo": foto}
                res = requests.post(url, data=payload, files=files, timeout=5)
        else:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": caption_text}
            res = requests.post(url, data=payload, timeout=5)
            
        hasil = res.json()
        if hasil.get("ok"):
            print("✅ [TELEGRAM] Laporan otomatis 1 detik berhasil mendarat!")
        else:
            print(f"❌ [TELEGRAM] Ditolak: {hasil.get('description')}")
            
    except Exception as e:
        print(f"❌ [TELEGRAM] Gagal koneksi: {e}")

def send_report(image_path, power_db, freq_mhz, persons, event_id):
    """Memicu thread latar belakang murni tanpa loop asyncio (Sangat Cepat)"""
    t = threading.Thread(
        target=_execute_send, 
        args=(image_path, power_db, freq_mhz, persons, event_id),
        daemon=True
    )
    t.start()