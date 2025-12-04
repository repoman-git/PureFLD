"""
FLD Plotting (Matplotlib)

Static publication-quality FLD visualizations.
"""

import matplotlib.pyplot as plt


def plot_fld(price, fld, long_crosses, short_crosses, upper=None, lower=None,
             title="FLD Plot"):
    """
    Plot FLD with price and crosses.
    
    Args:
        price: Price series
        fld: FLD series
        long_crosses: List of long cross timestamps
        short_crosses: List of short cross timestamps
        upper: Upper envelope (optional)
        lower: Lower envelope (optional)
        title: Chart title
    
    Returns:
        matplotlib figure
    
    Example:
        >>> from meridian_v2_1_2.hurst import FLDEngine
        >>> from meridian_v2_1_2.hurst.hurst_fld_plotting import plot_fld
        >>> 
        >>> engine = FLDEngine(period=40)
        >>> fld = engine.compute_fld(price)
        >>> crosses = engine.detect_crosses(price, fld)
        >>> 
        >>> plot_fld(price, fld, crosses['long_crosses'], crosses['short_crosses'])
    """
    plt.figure(figsize=(16, 8))
    
    plt.plot(price, color="black", linewidth=1.2, label="Price")
    plt.plot(fld, color="blue", linewidth=1.1, label=f"{fld.name}")
    
    if upper is not None:
        plt.plot(upper, color="dodgerblue", linestyle="--", alpha=0.5, label="Envelope High")
    
    if lower is not None:
        plt.plot(lower, color="dodgerblue", linestyle="--", alpha=0.5, label="Envelope Low")
    
    if long_crosses:
        plt.scatter(long_crosses, price.loc[long_crosses],
                    color="green", marker="^", s=100,
                    label="Long FLD crosses", zorder=5)
    
    if short_crosses:
        plt.scatter(short_crosses, price.loc[short_crosses],
                    color="red", marker="v", s=100,
                    label="Short FLD crosses", zorder=5)
    
    plt.title(title, fontsize=18)
    plt.xlabel("Date", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=11)
    plt.tight_layout()
    
    return plt.gcf()


