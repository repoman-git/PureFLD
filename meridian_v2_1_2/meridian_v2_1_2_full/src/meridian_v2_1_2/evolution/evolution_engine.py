"""
Evolution Engine - Genetic Algorithm for Strategy Optimization

Darwinian evolution of trading strategies through:
- Population-based search
- Mutation and crossover
- Multi-objective fitness evaluation
- Elitism (preserve best)
- Automatic improvement over generations
"""

import numpy as np
import random
from typing import Dict, Any, List, Tuple, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import copy


@dataclass
class Candidate:
    """Single strategy candidate in population"""
    params: Dict[str, Any]
    fitness: float = 0.0
    metrics: Dict[str, float] = None
    mc_stats: Dict[str, Any] = None
    generation: int = 0
    candidate_id: str = None
    
    def __post_init__(self):
        if self.candidate_id is None:
            self.candidate_id = f"cand_{random.randint(1000, 9999)}"
        if self.metrics is None:
            self.metrics = {}
        if self.mc_stats is None:
            self.mc_stats = {}


@dataclass
class EvolutionResult:
    """Complete results from evolution run"""
    evolution_id: str
    strategy_name: str
    generations: int
    population_size: int
    best_candidate: Candidate
    history: List[Dict[str, Any]]  # Best per generation
    final_population: List[Candidate]
    settings: Dict[str, Any]
    timestamp: str
    

def evolve_strategy(
    strategy_name: str,
    param_space: Dict[str, Any],
    population: int = 20,
    generations: int = 10,
    mutation_rate: float = 0.15,
    crossover_rate: float = 0.5,
    elite_size: int = 2,
    backtester_func: Optional[Callable] = None,
    fitness_func: Optional[Callable] = None,
    callback: Optional[Callable] = None
) -> EvolutionResult:
    """
    Evolve strategy parameters using genetic algorithm.
    
    Combines:
    - Phase 4: Backtesting
    - Phase 5: Monte Carlo & scoring
    - Phase 6: Genetic search
    
    Args:
        strategy_name: Name of strategy to evolve
        param_space: Parameter space definition (from param_spaces.py)
        population: Population size (default: 20)
        generations: Number of generations (default: 10)
        mutation_rate: Probability of mutation (default: 0.15)
        crossover_rate: Probability of crossover (default: 0.5)
        elite_size: Number of top candidates to preserve (default: 2)
        backtester_func: Custom backtest function (optional)
        fitness_func: Custom fitness function (optional)
        callback: Progress callback function (optional)
    
    Returns:
        EvolutionResult: Complete evolution run with best candidate
    
    Example:
        >>> from meridian_v2_1_2.evolution import evolve_strategy, FLD_PARAM_SPACE
        >>> result = evolve_strategy('FLD', FLD_PARAM_SPACE, population=20, generations=10)
        >>> print(f"Best fitness: {result.best_candidate.fitness:.2f}")
        >>> print(f"Best params: {result.best_candidate.params}")
    """
    
    evolution_id = f"evo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Use default functions if not provided
    if backtester_func is None:
        try:
            from meridian_v2_1_2.api import run_backtest
            backtester_func = run_backtest
        except ImportError:
            raise RuntimeError("No backtest function available")
    
    if fitness_func is None:
        fitness_func = _default_fitness_function
    
    print(f"🧬 Starting Evolution: {evolution_id}")
    print(f"   Strategy: {strategy_name}")
    print(f"   Population: {population}, Generations: {generations}")
    print(f"   Mutation Rate: {mutation_rate}, Crossover Rate: {crossover_rate}")
    
    # Initialize population
    current_population = _initialize_population(param_space, population)
    
    # Track best candidate overall
    all_time_best = None
    history = []
    
    # Evolution loop
    for gen in range(generations):
        print(f"\n🧬 Generation {gen + 1}/{generations}")
        
        # Evaluate fitness for all candidates
        for i, candidate in enumerate(current_population):
            if candidate.fitness == 0.0:  # Not yet evaluated
                candidate.fitness, candidate.metrics, candidate.mc_stats = fitness_func(
                    strategy_name,
                    candidate.params,
                    backtester_func
                )
                candidate.generation = gen
            
            # Progress callback
            if callback:
                callback(gen, i, population, candidate)
        
        # Sort by fitness (descending)
        current_population.sort(key=lambda c: c.fitness, reverse=True)
        
        # Track best of generation
        gen_best = current_population[0]
        history.append({
            'generation': gen,
            'best_fitness': gen_best.fitness,
            'best_params': gen_best.params,
            'mean_fitness': np.mean([c.fitness for c in current_population]),
            'std_fitness': np.std([c.fitness for c in current_population]),
            'candidate_id': gen_best.candidate_id
        })
        
        # Update all-time best
        if all_time_best is None or gen_best.fitness > all_time_best.fitness:
            all_time_best = copy.deepcopy(gen_best)
        
        print(f"   Best Fitness: {gen_best.fitness:.2f}")
        print(f"   Best Params: {gen_best.params}")
        
        # Stop if last generation
        if gen == generations - 1:
            break
        
        # Create next generation
        next_population = []
        
        # Elitism: Keep top candidates
        next_population.extend(copy.deepcopy(current_population[:elite_size]))
        
        # Fill rest with offspring
        while len(next_population) < population:
            # Tournament selection
            parent1 = _tournament_selection(current_population, k=3)
            parent2 = _tournament_selection(current_population, k=3)
            
            # Crossover
            if random.random() < crossover_rate:
                child = _crossover(parent1, parent2, param_space)
            else:
                child = copy.deepcopy(random.choice([parent1, parent2]))
            
            # Mutation
            if random.random() < mutation_rate:
                child = _mutate(child, param_space, mutation_rate)
            
            # Reset fitness (needs re-evaluation)
            child.fitness = 0.0
            child.candidate_id = f"cand_{random.randint(1000, 9999)}"
            
            next_population.append(child)
        
        current_population = next_population
    
    # Final evaluation for any unevaluated
    for candidate in current_population:
        if candidate.fitness == 0.0:
            candidate.fitness, candidate.metrics, candidate.mc_stats = fitness_func(
                strategy_name,
                candidate.params,
                backtester_func
            )
    
    current_population.sort(key=lambda c: c.fitness, reverse=True)
    
    print(f"\n🏆 Evolution Complete!")
    print(f"   Best Fitness: {all_time_best.fitness:.2f}")
    print(f"   From Generation: {all_time_best.generation}")
    
    return EvolutionResult(
        evolution_id=evolution_id,
        strategy_name=strategy_name,
        generations=generations,
        population_size=population,
        best_candidate=all_time_best,
        history=history,
        final_population=current_population,
        settings={
            'mutation_rate': mutation_rate,
            'crossover_rate': crossover_rate,
            'elite_size': elite_size,
            'param_space': param_space
        },
        timestamp=datetime.now().isoformat()
    )


def evaluate_candidate(
    strategy_name: str,
    params: Dict[str, Any],
    backtester_func: Optional[Callable] = None,
    include_mc: bool = True
) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    """
    Evaluate a single candidate strategy.
    
    Returns:
        (fitness_score, metrics, mc_stats)
    """
    return _default_fitness_function(strategy_name, params, backtester_func, include_mc)


# ============================================================================
# GENETIC ALGORITHM OPERATORS
# ============================================================================

def _initialize_population(param_space: Dict[str, Any], size: int) -> List[Candidate]:
    """Create initial random population"""
    population = []
    
    for _ in range(size):
        params = _random_params(param_space)
        population.append(Candidate(params=params))
    
    return population


def _random_params(param_space: Dict[str, Any]) -> Dict[str, Any]:
    """Generate random parameters from space"""
    params = {}
    
    for key, value_space in param_space.items():
        if isinstance(value_space, tuple):
            # Numeric range
            if isinstance(value_space[0], int):
                params[key] = random.randint(value_space[0], value_space[1])
            else:
                params[key] = random.uniform(value_space[0], value_space[1])
        elif isinstance(value_space, list):
            # Categorical choice
            params[key] = random.choice(value_space)
    
    return params


def _tournament_selection(population: List[Candidate], k: int = 3) -> Candidate:
    """Tournament selection - pick best from k random candidates"""
    tournament = random.sample(population, min(k, len(population)))
    return max(tournament, key=lambda c: c.fitness)


def _crossover(parent1: Candidate, parent2: Candidate, param_space: Dict[str, Any]) -> Candidate:
    """
    Single-point crossover for parameter dictionaries.
    
    Randomly combines parameters from two parents.
    """
    child_params = {}
    
    for key in param_space.keys():
        # Randomly choose from parent1 or parent2
        if random.random() < 0.5:
            child_params[key] = parent1.params.get(key, parent2.params.get(key))
        else:
            child_params[key] = parent2.params.get(key, parent1.params.get(key))
    
    return Candidate(params=child_params)


def _mutate(candidate: Candidate, param_space: Dict[str, Any], mutation_rate: float) -> Candidate:
    """
    Mutate candidate parameters.
    
    Each parameter has mutation_rate chance of being randomly changed.
    """
    mutated_params = copy.deepcopy(candidate.params)
    
    for key, value_space in param_space.items():
        if random.random() < mutation_rate:
            if isinstance(value_space, tuple):
                # Numeric mutation: Gaussian noise or random reset
                if random.random() < 0.7:
                    # Gaussian perturbation
                    current = mutated_params.get(key, (value_space[0] + value_space[1]) / 2)
                    range_size = value_space[1] - value_space[0]
                    noise = np.random.normal(0, range_size * 0.1)
                    new_value = current + noise
                    # Clip to bounds
                    new_value = max(value_space[0], min(value_space[1], new_value))
                    
                    if isinstance(value_space[0], int):
                        mutated_params[key] = int(round(new_value))
                    else:
                        mutated_params[key] = new_value
                else:
                    # Random reset
                    if isinstance(value_space[0], int):
                        mutated_params[key] = random.randint(value_space[0], value_space[1])
                    else:
                        mutated_params[key] = random.uniform(value_space[0], value_space[1])
            
            elif isinstance(value_space, list):
                # Categorical mutation: pick different option
                mutated_params[key] = random.choice(value_space)
    
    return Candidate(params=mutated_params)


# ============================================================================
# FITNESS EVALUATION
# ============================================================================

def _default_fitness_function(
    strategy_name: str,
    params: Dict[str, Any],
    backtester_func: Callable,
    include_mc: bool = False
) -> Tuple[float, Dict[str, float], Dict[str, Any]]:
    """
    Default multi-objective fitness function.
    
    Combines:
    - Sharpe ratio (primary)
    - Total return
    - Max drawdown (penalty)
    - Monte Carlo robustness (optional)
    
    Returns:
        (fitness_score, metrics_dict, mc_stats_dict)
    """
    
    try:
        # Run backtest
        result = backtester_func(
            strategy_name=strategy_name,
            params=params
        )
        
        metrics = result.metrics if hasattr(result, 'metrics') else {}
        
        # Extract key metrics
        sharpe = metrics.get('sharpe_ratio', 0)
        total_return = metrics.get('total_return', 0)
        max_dd = abs(metrics.get('max_drawdown', 0))
        
        # Base fitness: Sharpe-centric
        fitness = sharpe * 10  # Scale Sharpe to ~0-30 range
        
        # Bonus for returns
        fitness += total_return * 20  # Add ~0-20 for good returns
        
        # Penalty for drawdown
        if max_dd > 0.15:
            fitness -= (max_dd - 0.15) * 50  # Heavy penalty for >15% DD
        
        # Monte Carlo robustness (optional, expensive)
        mc_stats = {}
        if include_mc:
            try:
                from meridian_v2_1_2.simulation import monte_carlo_equity_simulation
                equity = result.equity_curve if hasattr(result, 'equity_curve') else []
                
                if len(equity) > 10:
                    mc_result = monte_carlo_equity_simulation(equity, n=100, block_size=10)
                    mc_stats = mc_result.stats
                    
                    # Bonus for low risk of ruin
                    if mc_result.risk_of_ruin < 0.05:
                        fitness += 10
                    elif mc_result.risk_of_ruin > 0.15:
                        fitness -= 10
            except:
                pass  # MC is optional
        
        # Ensure fitness is non-negative
        fitness = max(0, fitness)
        
        return fitness, metrics, mc_stats
        
    except Exception as e:
        # Failed evaluation gets zero fitness
        print(f"   Warning: Evaluation failed for {params}: {e}")
        return 0.0, {}, {}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_param_grid(param_space: Dict[str, Any], samples_per_param: int = 5) -> List[Dict[str, Any]]:
    """
    Create a grid of parameter combinations for initial exploration.
    
    Useful for seeding population with diverse candidates.
    """
    param_samples = {}
    
    for key, value_space in param_space.items():
        if isinstance(value_space, tuple):
            if isinstance(value_space[0], int):
                param_samples[key] = np.linspace(
                    value_space[0], 
                    value_space[1], 
                    samples_per_param, 
                    dtype=int
                ).tolist()
            else:
                param_samples[key] = np.linspace(
                    value_space[0], 
                    value_space[1], 
                    samples_per_param
                ).tolist()
        elif isinstance(value_space, list):
            param_samples[key] = value_space
    
    # Generate combinations (limited to avoid explosion)
    grid = []
    keys = list(param_samples.keys())
    
    # Simple sampling approach
    for _ in range(min(100, samples_per_param ** len(keys))):
        sample = {}
        for key in keys:
            sample[key] = random.choice(param_samples[key])
        grid.append(sample)
    
    return grid


def export_best_to_dict(result: EvolutionResult) -> Dict[str, Any]:
    """Export evolution result for serialization"""
    return {
        'evolution_id': result.evolution_id,
        'strategy_name': result.strategy_name,
        'generations': result.generations,
        'population_size': result.population_size,
        'best_candidate': {
            'params': result.best_candidate.params,
            'fitness': result.best_candidate.fitness,
            'metrics': result.best_candidate.metrics,
            'generation': result.best_candidate.generation,
            'candidate_id': result.best_candidate.candidate_id
        },
        'history': result.history,
        'settings': result.settings,
        'timestamp': result.timestamp
    }

