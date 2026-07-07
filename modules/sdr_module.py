# modules/sdr_module.py
import numpy as np
import logging
from rtlsdr import RtlSdr
import config
 
logger = logging.getLogger(__name__)
_sdr = None
 
def init_sdr():
    """Inisialisasi RTL-SDR. Panggil sekali saat startup."""
    global _sdr
    _sdr = RtlSdr()
    _sdr.sample_rate = config.SDR_SAMPLE_RATE
    _sdr.center_freq = config.SDR_FREQUENCY
    _sdr.gain = config.SDR_GAIN
    logger.info('SDR initialized: %.3f MHz, gain=%s',
                config.SDR_FREQUENCY/1e6, config.SDR_GAIN)
 
def read_power_db():
    """Baca samples dan hitung power dalam dBm. Return float."""
    samples = _sdr.read_samples(config.SDR_SAMPLES)
    power   = np.mean(np.abs(samples)**2)
    power_db= 10 * np.log10(power + 1e-10)
    return float(power_db)
 
def is_signal_detected(power_db):
    """True jika power melebihi threshold yang dikonfigurasi."""
    return power_db > config.SDR_THRESHOLD
 
def close_sdr():
    global _sdr
    if _sdr:
        _sdr.close()
        _sdr = None
        logger.info('SDR closed.')
