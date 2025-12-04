"""
Reward Tracking for Meridian v2.1.2

Track strategy performance and compute rewards for adaptive weighting.
"""

import pandas as pd
import numpy as np
from typing import Dict

from ..config import MetaLearningConfig


def compute_strategy_rewards(
    strategy_returns: Dict[str, pd.Series],
    config: MetaLearningConfig
) -> Dict[str, float]:
    """
    Compute reward scores for each strategy.
    
    Rewards are based on recent performance using configured metric:
    - MAR (return / |drawdown|)
    - Sharpe (risk-adjusted return)
    - Winrate
    - Expectancy
    
    Args:
        strategy_returns: Dict of {strategy_name: returns_series}
        config: Meta-learning configuration
    
    Returns:
        Dict[str, float]: Reward per strategy (normalized)
    """
    rewards = {}
    
    for strategy_name, returns in strategy_returns.items():
        if len(returns) < 2:
            rewards[strategy_name] = 0.0
            continue
        
        # Use recent performance
        lookback = min(config.reward_lookback, len(returns))
        recent_returns = returns.iloc[-lookback:]
        
        # Compute reward based on metric
        if config.reward_metric == "sharpe":
            reward = _compute_sharpe_reward(recent_returns)
        elif config.reward_metric == "mar":
            reward = _compute_mar_reward(recent_returns)
        elif config.reward_metric == "winrate":
            reward = _compute_winrate_reward(recent_returns)
        elif config.reward_metric == "expectancy":
            reward = _compute_expectancy_reward(recent_returns)
        else:
            reward = recent_returns.mean()  # Default to mean return
        
        rewards[strategy_name] = float(reward)
    
    return rewards


def _compute_sharpe_reward(returns: pd.Series) -> float:
    """Compute Sharpe-based reward"""
    if len(returns) < 2:
        return 0.0
    
    mean_return = returns.mean()
    std_return = returns.std()
    
    if std_return > 0:
        sharpe = mean_return / std_return
        return sharpe
    
    return 0.0


def _compute_mar_reward(returns: pd.Series) -> float:
    """Compute MAR-based reward (return / |drawdown|)"""
    if len(returns) < 2:
        return 0.0
    
    # Cumulative returns for drawdown
    cum_returns = (1 + returns).cumprod()
    cummax = cum_returns.cummax()
    drawdown = (cum_returns - cummax) / cummax
    max_dd = drawdown.min()
    
    total_return = cum_returns.iloc[-1] - 1
    
    if max_dd < 0:
        mar = total_return / abs(max_dd)
        return mar
    
    return total_return if total_return > 0 else 0.0


def _compute_winrate_reward(returns: pd.Series) -> float:
    """Compute winrate-based reward"""
    if len(returns) < 1:
        return 0.0
    
    positive_returns = (returns > 0).sum()
    total_periods = len(returns)
    
    winrate = positive_returns / total_periods
    return winrate


def _compute_expectancy_reward(returns: pd.Series) -> float:
    """Compute expectancy-based reward"""
    return returns.mean()


def track_rolling_rewards(
    strategy_returns: Dict[str, pd.Series],
    config: MetaLearningConfig
) -> pd.DataFrame:
    """
    Track rewards over time (rolling window).
    
    Returns:
        pd.DataFrame: Rewards per strategy over time
    """
    # Get common index
    index = list(strategy_returns.values())[0].index
    lookback = config.reward_lookback
    
    reward_history = {name: [] for name in strategy_returns.keys()}
    
    for i in range(len(index)):
        if i < lookback:
            # Not enough data yet
            for name in strategy_returns.keys():
                reward_history[name].append(0.0)
        else:
            # Compute rewards on window
            window_returns = {
                name: rets.iloc[i-lookback:i]
                for name, rets in strategy_returns.items()
            }
            
            rewards = compute_strategy_rewards(window_returns, config)
            
            for name in strategy_returns.keys():
                reward_history[name].append(rewards.get(name, 0.0))
    
    reward_df = pd.DataFrame(reward_history, index=index)
    return reward_df


