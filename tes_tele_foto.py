
import os
import requests
import config

def kirim_foto_test():
    token = "8829487691:AAHQ-Jneb12mJ-Eroy6gNrcFmB2gWEj2krg"
    chat_id = "1377452620"
    jalur_foto = r"D:\Mikrokontroler\sigint-station\data\captures\yolo_20260707_080726.jpg"
    
    if not os.path.exists(jalur_foto):
        print("? Eror: File foto target tidak ditemukan secara fisik di folder!")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    payload = {
        "chat_id": chat_id,
        "caption": "?? **LAPORAN INTEGRASI INTEGRAL**\n\nEvent: #99\nFreq: 145.0 MHz\nPower: -35.0 dBm\nPerson: 1\nStatus: Sistem Siap Pameran!"
    }
    
    print("?? Mencoba mengunggah foto taktis ke server Telegram...")
    try:
        with open(jalur_foto, "rb") as foto:
            files = {"photo": foto}
            # Kita kirim tanpa parse_mode MarkdownV2 untuk menghindari string nyangkut di Windows
            response = requests.post(url, data=payload, files=files)
            
        hasil = response.json()
        if hasil.get("ok"):
            print("? BERHASIL! Foto dan laporan deteksi mendarat di Telegram Anda!")
        else:
            print(f"? Telegram Menolak: {hasil.get("description")}")
    except Exception as e:
        print(f"? Gagal koneksi ke server: {e}")

if __name__ == "__main__":
    kirim_foto_test()

