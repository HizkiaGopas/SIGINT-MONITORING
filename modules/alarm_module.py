# modules/alarm_module.py — Python
# modules/alarm_module.py
# Alarm fisik via Serial ke Arduino + alarm suara via pygame
# FAULT-TOLERANT: gagal = log warning, bukan crash
 
import os
import threading
import logging
import config
 
logger = logging.getLogger(__name__)
 
# Flag status inisialisasi komponen
_serial_ok = False  # True jika koneksi Arduino berhasil
_pygame_ok = False  # True jika pygame audio berhasil
_ser       = None   # Objek pyserial.Serial
 
 
# ─────────────────────────────────────────────────────────
# INISIALISASI
# ─────────────────────────────────────────────────────────
 
def init_alarm():
    """
    Inisialisasi koneksi serial ke Arduino dan pygame audio.
    Aman dipanggil meski Arduino belum terhubung — tidak akan crash.
    """
    _init_serial()
    _init_audio()
 
 
def _init_serial():
    """Coba buka koneksi serial ke Arduino. Gagal = log warning saja."""
    global _serial_ok, _ser
 
    if not config.ARDUINO_ENABLED:
        logger.info('[ALARM] Arduino dinonaktifkan di config. Skip serial init.')
        return
 
    try:
        import serial
        _ser = serial.Serial(
            port     = config.ARDUINO_PORT,
            baudrate = config.ARDUINO_BAUD,
            timeout  = config.ARDUINO_TIMEOUT,
        )
        _serial_ok = True
        logger.info(
            '[ALARM] Serial OK — Arduino di %s @ %d baud.',
            config.ARDUINO_PORT, config.ARDUINO_BAUD
        )
    except Exception as e:
        # Tidak crash — hanya catat warning
        _serial_ok = False
        logger.warning('[ALARM] Koneksi serial gagal: %s', e)
        logger.warning('[ALARM] Periksa: apakah kabel USB Arduino sudah terpasang?')
        logger.warning('[ALARM] Port yang dicoba: %s', config.ARDUINO_PORT)
        logger.warning('[ALARM] Alarm fisik Arduino DINONAKTIFKAN untuk sesi ini.')
 
 
def _init_audio():
    """Coba inisialisasi pygame untuk suara. Gagal = log warning saja."""
    global _pygame_ok
    try:
        import pygame
        pygame.mixer.init()
        _pygame_ok = True
        logger.info('[ALARM] Pygame audio OK.')
    except Exception as e:
        _pygame_ok = False
        logger.warning('[ALARM] Pygame gagal init: %s', e)
        logger.warning('[ALARM] Alarm suara software dinonaktifkan.')
 
 
# ─────────────────────────────────────────────────────────
# PLAY ALARM — NON-BLOCKING
# ─────────────────────────────────────────────────────────
 
def play():
    """
    Picu alarm: kirim sinyal ke Arduino DAN play audio.
    Keduanya berjalan di thread terpisah — TIDAK MEMBLOKIR main loop.
    Sistem tetap responsif saat alarm sedang berbunyi.
    """
    threading.Thread(target=_send_serial, daemon=True).start()
    threading.Thread(target=_play_audio,  daemon=True).start()
 
 
def _send_serial():
    """Kirim karakter trigger ke Arduino via USB Serial."""
    if not _serial_ok or _ser is None:
        logger.debug('[ALARM] Serial tidak tersedia — skip kirim ke Arduino.')
        return
    try:
        # Encode string ke bytes lalu kirim
        signal_bytes = config.ARDUINO_SIGNAL.encode('utf-8')
        _ser.write(signal_bytes)
        _ser.flush()  # Pastikan data langsung dikirim
        logger.info(
            '[ALARM] Serial terkirim: "%s" ke Arduino di %s',
            config.ARDUINO_SIGNAL, config.ARDUINO_PORT
        )
    except Exception as e:
        logger.error('[ALARM] Gagal kirim serial ke Arduino: %s', e)
 
 
def _play_audio():
    """Play file WAV alarm melalui speaker. Fallback ke system beep."""
    if _pygame_ok and config.ALARM_FILE.exists():
        try:
            import pygame
            pygame.mixer.music.load(str(config.ALARM_FILE))
            pygame.mixer.music.play()
            logger.info('[ALARM] Audio alarm diputar.')
        except Exception as e:
            logger.error('[ALARM] Gagal play audio: %s', e)
    else:
        # Fallback: gunakan suara sistem Linux
        logger.debug('[ALARM] pygame tidak tersedia, fallback ke aplay.')
        os.system('aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null &')
 
 
def close_serial():
    """
    Tutup koneksi serial secara bersih saat sistem shutdown.
    Panggil di blok finally main.py.
    """
    global _ser, _serial_ok
    if _ser is not None and _ser.is_open:
        _ser.close()
        _serial_ok = False
        logger.info('[ALARM] Koneksi serial ke Arduino ditutup.')
