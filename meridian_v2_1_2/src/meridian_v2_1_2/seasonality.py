import pandas as pd
def compute_tdom_flags(index, favourable_days, unfavourable_days):
    days=index.day
    flags=[]
    for d in days:
        if d in favourable_days: flags.append(1)
        elif d in unfavourable_days: flags.append(-1)
        else: flags.append(0)
    return pd.Series(flags, index=index, name='tdom')
