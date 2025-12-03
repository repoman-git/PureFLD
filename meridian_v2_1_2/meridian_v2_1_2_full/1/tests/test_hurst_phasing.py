import pandas as pd
import numpy as np
from engine.hurst_phasing import HurstPhasingEngine


def test_hurst_phasing_basic():
    idx = pd.date_range('2020-01-01', periods=300, freq='D')
    price = pd.Series(100 + 5*np.sin(2*np.pi*idx.dayofyear/80), index=idx)
    engine = HurstPhasingEngine([80])
    res = engine.phase_cycle(price, 80)
    assert res['phase'].notna().sum() > 0
