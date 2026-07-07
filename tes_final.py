
import logging
import time
import os
import config
from modules import telegram_module, db_module, flask_server

logging.basicConfig(level=logging.INFO)

def main():
    # Jalur mutlak ke foto YOLO Anda yang terbukti valid
    jalur_foto = r"D:\Mikrokontroler\sigint-station\data\captures\yolo_20260707_080726.jpg"
    
    if not os.path.exists(jalur_foto):
        print("? Eror: Berkas foto target tidak ditemukan!")
        return

    print("?? [TEST] Memicu Pipeline Penuh...")
    print("1. Mendorong data visual ke Dasbor Browser (Port 3000)...")
    
    # Simulasikan data masuk ke Flask & WebSocket
    flask_server.emit_event({
        "event_id": 88,
        "time": "08:35:00",
        "date": "2026-07-07",
        "freq": 145.0,
        "power": -35.0,
        "persons": 1,
        "image": "/captures/yolo_20260707_080726.jpg"
    })
    
    print("2. Menembak Laporan + Foto Nyata ke Telegram Bot...")
    # Panggil fungsi sesuai urutan parameter asli modul Anda
    telegram_module.send_report(
        jalur_foto,   # image_path
        -35.0,        # power_db
        145.0,        # freq_mhz
        1,            # persons
        88            # event_id
    )
    
    print("? Menahan sistem 5 detik untuk proses unggah jaringan...")
    time.sleep(5)
    print("?? [SUKSES] Seluruh sektor selesai diuji!")

if __name__ == "__main__":
    main()

