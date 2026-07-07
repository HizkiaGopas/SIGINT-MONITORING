# modules/manual_trigger_module.py — Python
# modules/manual_trigger_module.py
# Listener keyboard background thread menggunakan pynput
# Mendeteksi tombol SPASI dan memberi sinyal ke main loop
 
import threading
import logging
from pynput import keyboard
import config
 
logger = logging.getLogger(__name__)
 
# threading.Event adalah 'bendera' yang thread-safe
# Main loop menunggu bendera ini, listener yang mengibarkannya
_trigger_event = threading.Event()
_listener      = None  # Objek listener pynput
 
 
def _resolve_key():
    """
    Konversi string nama tombol dari config menjadi objek pynput.
    Mendukung: 'space', 'enter', 'f1' hingga 'f12'.
    Default: keyboard.Key.space (tombol SPASI).
    """
    key_map = {
        'space': keyboard.Key.space,
        'enter': keyboard.Key.enter,
        'f1':    keyboard.Key.f1,
        'f2':    keyboard.Key.f2,
        'f3':    keyboard.Key.f3,
        'f4':    keyboard.Key.f4,
        'f5':    keyboard.Key.f5,
        'f6':    keyboard.Key.f6,
        'f7':    keyboard.Key.f7,
        'f8':    keyboard.Key.f8,
        'f9':    keyboard.Key.f9,
        'f10':   keyboard.Key.f10,
        'f11':   keyboard.Key.f11,
        'f12':   keyboard.Key.f12,
    }
    return key_map.get(config.MANUAL_TRIGGER_KEY.lower(), keyboard.Key.space)
 
 
def _on_press(key):
    """
    Callback yang dipanggil pynput setiap ada tombol ditekan.
    Hanya bereaksi terhadap tombol yang dikonfigurasi (default: SPASI).
    Menggunakan is_set() untuk mencegah double-trigger.
    """
    target_key = _resolve_key()
    if key == target_key:
        if not _trigger_event.is_set():
            # Set bendera — main loop akan mendeteksi ini
            logger.info(
                '[TRIGGER] Tombol %s ditekan — memicu deteksi...',
                config.MANUAL_TRIGGER_KEY.upper()
            )
            _trigger_event.set()
 
 
def init_manual_trigger():
    """
    Mulai listener keyboard di background thread.
    Panggil SEKALI saat startup sistem (dari main.py).
    Thread bersifat daemon: otomatis mati saat program utama berhenti.
    """
    global _listener
    _listener = keyboard.Listener(on_press=_on_press)
    _listener.daemon = True  # Mati otomatis bersama main program
    _listener.start()
    logger.info(
        '[TRIGGER] Listener aktif. Tombol trigger: [%s]',
        config.MANUAL_TRIGGER_KEY.upper()
    )
    # Tampilkan pesan panduan di terminal untuk operator
    print(f'\n{"=" * 50}')
    print(f'{config.MANUAL_TRIGGER_MSG}')
    print(f'{"=" * 50}\n')
 
 
def wait_for_trigger(timeout=None):
    """
    Fungsi blocking: berhenti di sini sampai tombol trigger ditekan.
    Tidak mengonsumsi CPU saat menunggu (event-driven, efisien).
 
    Args:
        timeout (float | None): Batas waktu tunggu dalam detik.
                                None = tunggu selamanya tanpa batas.
 
    Returns:
        bool: True jika trigger diterima, False jika timeout.
    """
    fired = _trigger_event.wait(timeout=timeout)
    if fired:
        # Reset bendera agar bisa menerima trigger berikutnya
        _trigger_event.clear()
    return fired
 
 
def stop_manual_trigger():
    """
    Hentikan listener keyboard secara bersih.
    Panggil di blok finally saat sistem shutdown.
    """
    global _listener
    if _listener is not None and _listener.is_alive():
        _listener.stop()
        logger.info('[TRIGGER] Listener dihentikan.')
