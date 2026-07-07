# modules/flask_server.py
# REST API + WebSocket SocketIO server untuk dashboard (Windows Optimized)
import os
import threading
import logging
from pathlib import Path
from flask import Flask, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import config
from modules import db_module

logger = logging.getLogger(__name__)


def _capture_url(path):
    if not path:
        return None
    return f"/captures/{Path(path).name}"

app = Flask(__name__)
CORS(app)

# Di Windows, kita hapus async_mode='eventlet' agar menggunakan native threading
socketio = SocketIO(app, cors_allowed_origins='*', ping_timeout=60, ping_interval=25)

# ─────────────────────────────────────────────────────────
# REST API ENDPOINTS
# ─────────────────────────────────────────────────────────

@app.route('/api/status')
def api_status():
    return jsonify({
        'status':    'MONITORING',
        'mode':      'DEMO' if config.MANUAL_TRIGGER_MODE else 'SDR',
        'freq_mhz':  config.SDR_FREQUENCY / 1e6,
        'threshold': config.YOLO_CONF,
    })

@app.route('/api/events')
def api_events():
    events = db_module.get_recent_events(20)
    normalized = [
        {
            **event,
            'image': _capture_url(event.get('image_path'))
        }
        for event in events
    ]
    return jsonify(normalized)

@app.route('/captures/<path:filename>')
def serve_captures(filename):
    custom_dir = r"D:\Mikrokontroler\sigint-station\data\captures"
    return send_from_directory(custom_dir, filename)

# ─────────────────────────────────────────────────────────
# WEBSOCKET — PUSH UPDATE KE DASHBOARD
# ─────────────────────────────────────────────────────────

def emit_event(event_data: dict):
    socketio.emit('signal_detected', event_data)
    logger.info('[FLASK] Event berhasil didorong ke dashboard: event_id=%s', event_data.get('event_id'))

# ─────────────────────────────────────────────────────────
# START SERVER
# ─────────────────────────────────────────────────────────

def start_server():
    """
    Jalankan Flask+SocketIO di background thread menggunakan server Werkzeug standar.
    """
    def _run():
        # allow_unsafe_werkzeug=True wajib di Windows agar bisa jalan di dalam background thread
        socketio.run(
            app,
            host        = config.FLASK_HOST,
            port        = config.FLASK_PORT,
            debug       = False,
            use_reloader= False,
            allow_unsafe_werkzeug=True
        )

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    logger.info('[FLASK] Server aktif di %s:%d (Native Threading Mode)', config.FLASK_HOST, config.FLASK_PORT)