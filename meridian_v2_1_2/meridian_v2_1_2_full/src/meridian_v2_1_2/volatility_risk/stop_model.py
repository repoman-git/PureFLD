"""Stop Distance Model"""
import pandas as pd

class StopDistanceModel:
    def compute(self, catr, vcycle, rws):
        stop = (1.0 * catr + 0.3 * vcycle + 0.2 * rws).fillna(0)
        return stop.rename("stop_distance")

