
import logging
import time
import os
import config
from modules import telegram_module

logging.basicConfig(level=logging.INFO)

def main():
    # Jalur mutlak ke foto YOLO Anda yang ada di folder captures
    jalur_foto = r"D:\Mikrokontroler\sigint-station\data\captures\yolo_20260707_080726.jpg"
    
    if not os.path.exists(jalur_foto):
        print("? Eror: File foto target tidak ditemukan di folder! Periksa nama filenya.")
        return

    print("?? Memicu pengiriman laporan + FOTO NYATA ke Telegram...")
    
    # Mengirimkan parameter lengkap dengan file gambar asli
    telegram_module.send_report(
        jalur_foto,   # image_path resmi
        -35.0,        # power_db
        145.0,        # freq_mhz
        1,            # persons
        1             # event_id
    )
    
    print("? Menahan terminal 5 detik agar background thread selesai mengunggah gambar...")
    time.sleep(5)
    print("?? Eksekusi selesai. Cek aplikasi Telegram Anda!")

if __name__ == "__main__":
    main()

