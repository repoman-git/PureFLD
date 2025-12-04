"""Strategy Genome - DNA encoding of trading strategies"""
import numpy as np
import random
from typing import Dict

class StrategyGenome:
    """Defines the 'DNA' of a trading strategy using parameter genes"""
    
    def __init__(self, genes: Dict = None):
        if genes is None:
            self.genes = {
                "fld_offset": random.uniform(0.5, 3.0),
                "vtl_slope_tol": random.uniform(0.1, 2.0),
                "cycle_amp_min": random.uniform(0.1, 2.0),
                "vol_thresh": random.uniform(0.2, 2.0),
                "rws_limit": random.uniform(0.1, 2.0),
                "forecast_slope": random.uniform(-1.0, 1.0),
                "regime_filter": random.choice([0, 1, 2, 3, 4])
            }
        else:
            self.genes = genes
    
    def mutate(self, rate: float = 0.1):
        """Mutate genome with given rate"""
        new_genes = self.genes.copy()
        for k in new_genes:
            if random.random() < rate:
                if k == "regime_filter":
                    new_genes[k] = random.choice([0, 1, 2, 3, 4])
                else:
                    new_genes[k] += np.random.normal(0, 0.1)
        return StrategyGenome(new_genes)
    
    def crossover(self, other):
        """Crossover with another genome"""
        new_genes = {}
        for k in self.genes:
            new_genes[k] = random.choice([self.genes[k], other.genes[k]])
        return StrategyGenome(new_genes)
    
    def __repr__(self):
        return f"Genome({', '.join(f'{k}={v:.2f}' for k, v in self.genes.items())})"

