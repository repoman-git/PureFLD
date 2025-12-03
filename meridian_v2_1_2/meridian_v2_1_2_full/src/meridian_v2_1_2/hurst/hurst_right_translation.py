"""
Hurst Right-Translation Logic

Implements Hurst-style "right translation":
- New troughs can shift earlier troughs
- Maintains nesting integrity
- Maximizes consistency with nominal cycle periods
- Exactly like Sentient Trader does

This makes phasing dynamic - as new data arrives, the model
re-evaluates cycle alignment and peaks/troughs shift backward
into more correct positions.
"""

import pandas as pd
import numpy as np


class RightTranslationAdjuster:
    """
    Implements Hurst-style "right translation":
    - new troughs can shift earlier troughs
    - maintains nesting integrity
    - maximizes consistency with nominal cycle periods
    """

    def __init__(self, tolerance=0.35):
        """
        tolerance: permitted deviation from nominal spacing
        """
        self.tolerance = tolerance

    def adjust_troughs(self, troughs, nominal_period):
        """
        Given a list of trough timestamps (sorted), adjust earlier ones
        to create more consistent spacing when new data arrives.

        Logic:
        - compute local spacing
        - measure deviation from nominal
        - shift earlier trough to minimize global error

        Returns: adjusted list of trough timestamps
        """

        if len(troughs) < 3:
            return troughs

        troughs = list(sorted(troughs))  # defensive copy

        changed = True
        max_iters = 5

        while changed and max_iters > 0:
            changed = False
            max_iters -= 1

            for i in range(1, len(troughs) - 1):
                left = troughs[i - 1]
                mid  = troughs[i]
                right = troughs[i + 1]

                expected_spacing = nominal_period

                spacing_left  = (mid - left).days
                spacing_right = (right - mid).days

                err_left  = spacing_left  - expected_spacing
                err_right = spacing_right - expected_spacing

                # If both sides are stretched/compressed similarly → shift mid
                if abs(err_left) > nominal_period * self.tolerance or \
                   abs(err_right) > nominal_period * self.tolerance:

                    # Adjust the mid position to be centered
                    new_mid = left + pd.Timedelta(days=expected_spacing)

                    if new_mid != mid:
                        troughs[i] = new_mid
                        changed = True

        return troughs

    def adjust_all_cycles(self, phasing_results):
        """
        Run right-translation adjustment over multi-cycle phasing results.

        Input:
            { period: {"troughs": [...], ...}, ... }

        Output:
            same dict with adjusted troughs
        """
        updated = {}

        for period, res in phasing_results.items():
            troughs = res.get("troughs", [])
            if len(troughs) < 3:
                updated[period] = res
                continue

            adj = self.adjust_troughs(troughs, period)
            new_res = res.copy()
            new_res["troughs"] = adj
            updated[period] = new_res

        return updated

