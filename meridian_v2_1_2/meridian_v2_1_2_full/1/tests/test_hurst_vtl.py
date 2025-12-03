import pandas as pd
import numpy as np
from engine.hurst_vtl import HurstVTLBuilder, HurstVTLBreakDetector


def test_hurst_vtl_basic():
    idx = pd.date_range('2020-01-01', periods=50, freq='D')
    price = pd.Series(np.linspace(100, 120, len(idx)), index=idx)
    troughs = [idx[10], idx[30]]
    builder = HurstVTLBuilder()
    vtl = builder.build_vtl(price, troughs)
    assert vtl.notna().sum() > 0

    detector = HurstVTLBreakDetector()
    price.iloc[-1] = price.iloc[-1] - 10
    breaks = detector.find_breaks(price, vtl, direction="uptrend")
    assert isinstance(breaks, list)
