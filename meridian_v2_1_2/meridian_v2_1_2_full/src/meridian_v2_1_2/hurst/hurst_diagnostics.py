import numpy as np
import pandas as pd
from typing import List


class HurstDiagnostics:
    def spacing_stats(self, troughs: List[pd.Timestamp], nominal_period: int) -> pd.DataFrame:
        if len(troughs) < 2:
            return pd.DataFrame(columns=["spacing_days", "ratio_to_nominal"])
        idx = pd.Index(troughs)
        spacing_days = np.diff(idx.astype("int64") // 10**9) / 86400.0
        ratios = spacing_days / nominal_period
        return pd.DataFrame({"spacing_days": spacing_days, "ratio_to_nominal": ratios})

    def nesting_distances(self, inner_troughs: List[pd.Timestamp],
                          outer_troughs: List[pd.Timestamp]) -> pd.DataFrame:
        if len(inner_troughs) == 0 or len(outer_troughs) == 0:
            return pd.DataFrame(columns=["outer_trough", "min_distance_days"])
        inner_idx = pd.Index(inner_troughs)
        rows = []
        for ot in outer_troughs:
            diffs = (inner_idx - ot).days
            min_dist = float(np.min(np.abs(diffs)))
            rows.append({"outer_trough": ot, "min_distance_days": min_dist})
        return pd.DataFrame(rows)

    def phase_conditioned_returns(self, price: pd.Series, phase: pd.Series,
                                  forward_horizon: int = 10, bins: int = 10) -> pd.DataFrame:
        df = pd.DataFrame({"price": price, "phase": phase}).dropna()
        df["fwd_ret"] = df["price"].shift(-forward_horizon) / df["price"] - 1.0
        df = df.dropna()
        df["phase_bin"] = (df["phase"].clip(0, 0.9999) * bins).astype(int)
        stats = df.groupby("phase_bin")["fwd_ret"].agg(["mean", "count"])
        stats["phase_center"] = (stats.index + 0.5) / bins
        return stats.reset_index(drop=True)
