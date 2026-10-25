"""Measurements on ngspice waveforms."""

import numpy as np
from spicelib import RawRead

GROUND = {"GND", "0"}


def time_axis(raw: RawRead) -> np.ndarray:
    return np.abs(np.asarray(raw.get_axis()))


def voltage(raw: RawRead, net: str) -> np.ndarray:
    if net in GROUND:
        return np.zeros(len(raw.get_axis()))
    return np.asarray(raw.get_trace(f"V({net})").get_wave())


def rms(t: np.ndarray, v: np.ndarray, window: tuple[float, float]) -> float:
    m = (t >= window[0]) & (t <= window[1])
    return float(np.sqrt(np.trapezoid(v[m] ** 2, t[m]) / (t[m][-1] - t[m][0])))
