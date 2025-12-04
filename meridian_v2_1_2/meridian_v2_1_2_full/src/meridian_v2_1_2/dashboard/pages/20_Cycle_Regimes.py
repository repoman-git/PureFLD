"""
Cycle Regime Classifier Dashboard Page

Stage 2 integration into Meridian dashboard.

Author: Meridian Team
Date: December 4, 2025
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from meridian_v2_1_2.regimes.regime_dashboard import run_regime_dashboard

if __name__ == "__main__":
    run_regime_dashboard()

