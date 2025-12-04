"""Genetic Strategy Engine - Main evolution loop"""
import random
import numpy as np
from typing import Tuple, List
from .genome import StrategyGenome
from .rule_library import RuleLibrary
from .backtester import StrategyBacktester
from .evaluator import StrategyEvaluator

class GeneticStrategyEngine:
    """Evolves strategies via genetic programming"""
    
    def __init__(self, population_size: int = 20, generations: int = 10, mutation_rate: float = 0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.library = RuleLibrary()
        self.evaluator = StrategyEvaluator()
        self.backtester = StrategyBacktester()
    
    def evolve(self, price, phasing=None, fld=None, vtl=None, vol_df=None, forecast=None) -> Tuple[StrategyGenome, List[float]]:
        """Run genetic evolution"""
        population = [StrategyGenome() for _ in range(self.population_size)]
        history = []
        
        for g in range(self.generations):
            scored = []
            
            for genome in population:
                try:
                    signals = self.library.generate_signals(price, phasing, fld, vtl, vol_df, forecast, genome)
                    equity = self.backtester.run(price, signals)
                    fitness = self.evaluator.evaluate(equity)
                    scored.append((genome, fitness))
                except Exception:
                    scored.append((genome, 0.0))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            best = scored[:5]
            history.append(best[0][1])
            
            print(f"Gen {g+1}/{self.generations}: Best fitness = {best[0][1]:.4f}")
            
            # Next generation
            next_pop = [g for g, f in best[:2]]  # Elitism
            
            while len(next_pop) < self.population_size:
                parents = random.sample(best, 2)
                child = parents[0][0].crossover(parents[1][0])
                child = child.mutate(self.mutation_rate)
                next_pop.append(child)
            
            population = next_pop
        
        return scored[0][0], history

