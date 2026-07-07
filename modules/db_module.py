# modules/db_module.py — Python
# modules/db_module.py
# Simpan semua event, capture, dan log ke database SQLite
# Data tidak hilang meski RPi5 di-restart
 
import sqlite3
import logging
from datetime import datetime
import config
 
logger = logging.getLogger(__name__)
 
 
def get_connection():
    """
    Buka koneksi baru ke database SQLite.
    check_same_thread=False diperlukan karena koneksi diakses dari
    beberapa thread (main loop dan Flask server).
    """
    conn = sqlite3.connect(str(config.DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Hasil query bisa diakses seperti dict
    return conn
 
 
def init_db():
    """
    Buat tabel database jika belum ada.
    Aman dipanggil berulang kali — tidak akan menghapus data yang ada.
    """
    with get_connection() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  TEXT    NOT NULL,
                frequency  REAL    NOT NULL,
                power_db   REAL    NOT NULL,
                persons    INTEGER DEFAULT 0,
                image_path TEXT,
                sent_tg    INTEGER DEFAULT 0
            );
 
            CREATE TABLE IF NOT EXISTS captures (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id   INTEGER REFERENCES events(id),
                timestamp  TEXT    NOT NULL,
                path       TEXT    NOT NULL,
                persons    INTEGER DEFAULT 0
            );
 
            CREATE TABLE IF NOT EXISTS system_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  TEXT    NOT NULL,
                level      TEXT    NOT NULL,
                message    TEXT    NOT NULL
            );
        ''')
    logger.info('[DB] Database diinisialisasi: %s', config.DB_PATH)
 
 
def save_event(frequency, power_db, persons, image_path):
    """
    Simpan satu event deteksi ke database.
 
    Args:
        frequency  (float): Frekuensi sinyal dalam MHz.
        power_db   (float): Kekuatan sinyal dalam dBm.
        persons    (int):   Jumlah orang terdeteksi YOLOv8.
        image_path (str):   Path file foto hasil capture.
 
    Returns:
        int: ID event yang baru disimpan.
    """
    ts = datetime.now().isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            '''INSERT INTO events (timestamp, frequency, power_db, persons, image_path)
               VALUES (?, ?, ?, ?, ?)''',
            (ts, frequency, power_db, persons, str(image_path) if image_path else None)
        )
        event_id = cur.lastrowid
 
        # Simpan juga ke tabel captures jika ada gambar
        if image_path:
            conn.execute(
                '''INSERT INTO captures (event_id, timestamp, path, persons)
                   VALUES (?, ?, ?, ?)''',
                (event_id, ts, str(image_path), persons)
            )
 
    logger.info(
        '[DB] Event #%d disimpan: %.1f dBm, %d orang.',
        event_id, power_db, persons
    )
    return event_id
 
 
def get_recent_events(limit=20):
    """Ambil event terbaru, diurutkan dari yang paling baru."""
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM events ORDER BY id DESC LIMIT ?',
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
 
 
def mark_sent_telegram(event_id):
    """Tandai bahwa laporan Telegram sudah berhasil dikirim."""
    with get_connection() as conn:
        conn.execute(
            'UPDATE events SET sent_tg = 1 WHERE id = ?',
            (event_id,)
        )
