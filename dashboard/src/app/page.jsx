// dashboard/src/app/page.jsx — React/Next.js
// dashboard/src/app/page.jsx
// Dashboard real-time Tactical SIGINT Station
// Koneksi WebSocket ke Flask di RPi5 — update otomatis saat ada deteksi

'use client';

import { useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';

// URL Flask server di RPi5 — ambil dari environment variable
// Isi di file dashboard/.env.local:
// NEXT_PUBLIC_FLASK_URL=http://192.168.1.100:5000
const FLASK_URL = process.env.NEXT_PUBLIC_FLASK_URL || 'http://localhost:5000';

export default function Dashboard() {
    // ── STATE ──────────────────────────────────────────────
    const [events, setEvents] = useState([]);   // Daftar semua event
    const [latest, setLatest] = useState(null); // Event terakhir (untuk tampilan utama)
    const [status, setStatus] = useState('MENGHUBUNGKAN...');
    const [isAlert, setIsAlert] = useState(false); // Efek flash merah saat ada deteksi
    const socketRef = useRef(null);

    // ── EFFECT: Koneksi WebSocket & Load Riwayat ──────────
    useEffect(() => {
        // 1. Load riwayat event dari REST API saat pertama kali buka
        fetch(`${FLASK_URL}/api/events`)
            .then(r => r.json())
            .then(data => {
                setEvents(data);
                if (data.length > 0) setLatest(data[0]);
            })
            .catch(err => console.warn('Gagal load riwayat:', err));

        // 2. Hubungkan WebSocket ke Flask SocketIO
        const socket = io(FLASK_URL, {
            transports: ['websocket', 'polling'],
            reconnectionDelay: 2000,
        });
        socketRef.current = socket;

        socket.on('connect', () => {
            console.log('WebSocket terhubung ke RPi5.');
            setStatus('MONITORING');
        });

        socket.on('disconnect', () => {
            console.warn('WebSocket terputus.');
            setStatus('TERPUTUS');
        });

        socket.on('connect_error', (err) => {
            console.error('Koneksi error:', err.message);
            setStatus('ERROR KONEKSI');
        });

        // 3. Tangani event deteksi baru yang dipush dari RPi5
        socket.on('signal_detected', (data) => {
            console.log('Event baru diterima:', data);

            // Update latest event (tampilan foto utama)
            setLatest(data);

            // Tambahkan ke daftar event (maksimal 50 entry)
            setEvents(prev => [data, ...prev].slice(0, 50));

            // Efek flash merah selama 1.5 detik
            setIsAlert(true);
            setTimeout(() => setIsAlert(false), 1500);
        });

        // Cleanup saat komponen di-unmount
        return () => socket.disconnect();
    }, []);

    // ── HELPER: Format timestamp ───────────────────────────
    const formatTime = (e) =>
        e.time || (e.timestamp ? e.timestamp.substring(11, 19) : '--:--:--');

    const formatDate = (e) =>
        e.date || (e.timestamp ? e.timestamp.substring(0, 10) : '----/--/--');

    // ── RENDER ─────────────────────────────────────────────
    return (
        <div
            className={`min-h-screen bg-[#0D0D1A] text-white font-mono p-3
                  transition-all duration-300
                  ${isAlert ? 'ring-4 ring-red-500 ring-inset' : ''}`}
        >

            {/* ── HEADER ── */}
            <div className='border-b border-orange-500 pb-2 mb-4 flex justify-between items-center'>
                <div>
                    <h1 className='text-orange-400 text-lg font-bold tracking-widest'>
                        ⚡ TACTICAL SIGINT STATION
                    </h1>
                    <p className='text-gray-500 text-xs mt-0.5'>
                        Visual Logging & AI Detection Dashboard
                    </p>
                </div>
                <div className='text-right'>
                    <span
                        className={`text-sm font-bold px-2 py-1 rounded
              ${status === 'MONITORING'
                                ? 'bg-green-900 text-green-300'
                                : 'bg-red-900 text-red-300'}`}
                    >
                        ● {status}
                    </span>
                    <p className='text-gray-600 text-xs mt-1'>
                        {FLASK_URL}
                    </p>
                </div>
            </div>

            <div className='grid grid-cols-1 lg:grid-cols-3 gap-3'>

                {/* ── PANEL KIRI: Foto Deteksi Terakhir ── */}
                <div className='lg:col-span-2'>

                    {/* Alert Banner */}
                    {isAlert && (
                        <div className='bg-red-900 border border-red-500 text-red-200
                           text-center py-2 mb-3 rounded text-sm font-bold
                           animate-pulse'>
                            🚨 DETEKSI BARU — SISTEM AKTIF
                        </div>
                    )}

                    {/* Foto + Info Event Terakhir */}
                    <div className='bg-[#1A1A2E] border border-orange-800 rounded p-3 mb-3'>
                        <p className='text-orange-400 font-bold text-xs mb-2 tracking-widest'>
                            LAST CAPTURE
                        </p>

                        {latest ? (
                            <>
                                {/* Grid info event */}
                                <div className='grid grid-cols-2 sm:grid-cols-4 gap-2 mb-3'>
                                    {[
                                        { label: 'WAKTU', val: formatTime(latest) },
                                        { label: 'TANGGAL', val: formatDate(latest) },
                                        { label: 'POWER', val: `${latest.power ?? latest.power_db ?? '--'} dBm` },
                                        { label: 'ORANG', val: `${latest.persons ?? '--'} terdeteksi` },
                                    ].map(({ label, val }) => (
                                        <div key={label} className='bg-[#0F3460] rounded p-2 text-center'>
                                            <p className='text-gray-400 text-xs'>{label}</p>
                                            <p className='text-cyan-300 font-bold text-sm mt-0.5'>{val}</p>
                                        </div>
                                    ))}
                                </div>

                                {/* Foto hasil deteksi */}
                                {latest.image ? (
                                    <div className='relative'>
                                        <img
                                            src={`${FLASK_URL}${latest.image}`}
                                            alt='Foto deteksi terakhir'
                                            className='w-full rounded border border-orange-900
                                 max-h-72 object-contain bg-black'
                                        />
                                        <div className='absolute top-2 left-2 bg-orange-600
                                    text-white text-xs px-2 py-0.5 rounded'>
                                            YOLOv8 ANNOTATED
                                        </div>
                                    </div>
                                ) : (
                                    <div className='h-40 flex items-center justify-center
                                  border border-dashed border-gray-700 rounded'>
                                        <p className='text-gray-600 text-sm'>Foto tidak tersedia</p>
                                    </div>
                                )}
                            </>
                        ) : (
                            <div className='h-52 flex flex-col items-center justify-center
                              border border-dashed border-gray-700 rounded gap-2'>
                                <p className='text-gray-500 text-3xl'>📷</p>
                                <p className='text-gray-600 text-sm'>Menunggu deteksi pertama...</p>
                                <p className='text-gray-700 text-xs'>Tekan SPASI di keyboard RPi5</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* ── PANEL KANAN: Event Log ── */}
                <div className='bg-[#1A1A2E] border border-gray-700 rounded p-3
                        flex flex-col'>
                    <p className='text-cyan-400 font-bold text-xs mb-2 tracking-widest'>
                        EVENT LOG ({events.length})
                    </p>

                    <div className='flex-1 overflow-y-auto space-y-1 max-h-96 lg:max-h-full'>
                        {events.length === 0 ? (
                            <p className='text-gray-600 text-xs text-center mt-4'>
                                Belum ada event...
                            </p>
                        ) : (
                            events.map((e, i) => (
                                <div
                                    key={i}
                                    className={`text-xs border-b border-gray-800 pb-1
                    ${i === 0 && isAlert ? 'text-orange-300' : 'text-gray-400'}`}
                                >
                                    <span className='text-gray-600'>[{formatTime(e)}]</span>
                                    {' '}
                                    <span className='text-cyan-400'>
                                        {e.freq ?? e.frequency ?? '--'} MHz
                                    </span>
                                    {' | '}
                                    <span className='text-orange-400'>
                                        {e.power ?? e.power_db ?? '--'} dBm
                                    </span>
                                    {' | '}
                                    <span className='text-green-400'>
                                        P:{e.persons ?? '--'}
                                    </span>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Stats ringkas */}
                    <div className='border-t border-gray-700 pt-2 mt-2 grid grid-cols-2 gap-2'>
                        <div className='text-center'>
                            <p className='text-orange-400 font-bold text-lg'>{events.length}</p>
                            <p className='text-gray-600 text-xs'>Total Event</p>
                        </div>
                        <div className='text-center'>
                            <p className='text-green-400 font-bold text-lg'>
                                {events.reduce((s, e) => s + (e.persons || 0), 0)}
                            </p>
                            <p className='text-gray-600 text-xs'>Total Orang</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* ── FOOTER ── */}
            <div className='mt-3 text-center text-gray-700 text-xs border-t
                      border-gray-800 pt-2'>
                Tactical SIGINT & Visual Logging Station — Mode Demo
                {' | '} RPi5 + Arduino Uno + YOLOv8
            </div>
        </div>
    );
}
