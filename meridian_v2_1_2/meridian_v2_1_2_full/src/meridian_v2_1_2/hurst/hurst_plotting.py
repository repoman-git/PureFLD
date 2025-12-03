import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Optional


def plot_hurst_view(price: pd.Series,
                    troughs: List[pd.Timestamp],
                    vtl: Optional[pd.Series] = None,
                    breaks: Optional[List[pd.Timestamp]] = None,
                    title: str = "Hurst Phasing View"):
    plt.figure(figsize=(14, 7))
    plt.plot(price, label="Price")
    if troughs:
        plt.scatter(troughs, price.loc[troughs], color="red", label="Troughs")
    if vtl is not None and not vtl.isna().all():
        plt.plot(vtl, linestyle="--", label="VTL")
    if breaks:
        plt.scatter(breaks, price.loc[breaks], color="black", marker="x", s=80, label="VTL breaks")
    plt.legend()
    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_phase_vs_price(price: pd.Series, phase: pd.Series, period: int, title: str = "Phase vs Price"):
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(price, label="Price", color="tab:blue")
    ax1.set_ylabel("Price", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.plot(phase, label="Phase (0..1)", color="tab:orange", alpha=0.7)
    ax2.set_ylabel("Phase (0..1)", color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")

    plt.title(f"{title} – Period ~ {period}")
    fig.tight_layout()
    plt.show()
