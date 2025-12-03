import numpy as np
import pandas as pd
from scipy.signal import hilbert


class HurstPhasingEngine:
    def __init__(self, nominal_periods, smooth_factor: float = 0.5,
                 phase_wrap_window: float = 0.15, spacing_tolerance: float = 0.4):
        self.nominal_periods = nominal_periods
        self.smooth_factor = smooth_factor
        self.phase_wrap_window = phase_wrap_window
        self.spacing_tolerance = spacing_tolerance

    def _compute_phase(self, price: pd.Series, period: int) -> pd.Series:
        win = max(3, int(period * self.smooth_factor))
        smooth = price.rolling(window=win, min_periods=win).mean().dropna()
        if len(smooth) < period * 3:
            return pd.Series(index=price.index, dtype=float)
        analytic = hilbert(smooth.values)
        angles = np.angle(analytic)
        phase = (angles + np.pi) / (2 * np.pi)
        phase = pd.Series(phase, index=smooth.index)
        return phase.reindex(price.index)

    def _detect_troughs(self, price: pd.Series, phase: pd.Series, period: int):
        troughs = []
        last_trough_idx = None
        phase_prev = phase.shift(1)
        candidates = phase[(phase_prev > (1 - self.phase_wrap_window)) &
                           (phase < self.phase_wrap_window)].dropna()
        for ts in candidates.index:
            start = ts - pd.Timedelta(days=period)
            end = ts + pd.Timedelta(days=period)
            window = price.loc[start:end]
            if len(window) == 0:
                continue
            trough_time = window.idxmin()
            if last_trough_idx is not None:
                delta_days = (trough_time - last_trough_idx).days
                if delta_days < period * (1 - self.spacing_tolerance):
                    continue
            troughs.append(trough_time)
            last_trough_idx = trough_time
        troughs = sorted(list(dict.fromkeys(troughs)))
        return troughs

    def phase_cycle(self, price: pd.Series, period: int) -> dict:
        phase = self._compute_phase(price, period)
        if phase.isna().all():
            return {"period": period,
                    "phase": phase,
                    "angles": pd.Series(index=price.index, dtype=float),
                    "troughs": []}
        angles = phase * 360.0
        troughs = self._detect_troughs(price, phase, period)
        return {"period": period, "phase": phase, "angles": angles, "troughs": troughs}

    def phase_all(self, price: pd.Series) -> dict:
        return {p: self.phase_cycle(price, p) for p in self.nominal_periods}
