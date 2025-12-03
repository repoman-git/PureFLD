import pandas as pd
from typing import List


class HurstVTLBuilder:
    def build_vtl(self, price: pd.Series, troughs: List[pd.Timestamp]) -> pd.Series:
        vtl = pd.Series(index=price.index, dtype=float)
        if len(troughs) < 2:
            return vtl
        t1, t2 = troughs[-2], troughs[-1]
        if t1 not in price.index or t2 not in price.index:
            return vtl
        y1, y2 = price.loc[t1], price.loc[t2]
        i1 = price.index.get_loc(t1)
        i2 = price.index.get_loc(t2)
        if isinstance(i1, slice) or isinstance(i2, slice):
            return vtl
        for i in range(i1, len(price)):
            if i2 == i1:
                v = y2
            else:
                v = y1 + (y2 - y1) * (i - i1) / (i2 - i1)
            vtl.iloc[i] = v
        return vtl


class HurstVTLBreakDetector:
    def find_breaks(self, price: pd.Series, vtl: pd.Series,
                    direction: str = "uptrend") -> list:
        breaks = []
        for i in range(1, len(price)):
            p_prev, p_cur = price.iloc[i - 1], price.iloc[i]
            v_prev, v_cur = vtl.iloc[i - 1], vtl.iloc[i]
            if pd.isna(v_prev) or pd.isna(v_cur):
                continue
            if direction == "uptrend":
                if p_cur < v_cur and p_prev >= v_prev:
                    breaks.append(price.index[i])
            else:
                if p_cur > v_cur and p_prev <= v_prev:
                    breaks.append(price.index[i])
        return breaks
