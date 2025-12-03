"""
Reinforcement Learning Environment

Gym-style environment for strategy parameter optimization.
Agent interacts by proposing parameter modifications and receives
rewards based on backtest performance.
"""

import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from dataclasses import dataclass
import copy


@dataclass
class RLState:
    """Current state representation"""
    current_params: Dict[str, Any]
    recent_rewards: List[float]
    episode_step: int
    best_reward_so_far: float


class BacktestEnv:
    """
    Gym-style environment for strategy parameter optimization.
    
    The agent takes actions (parameter modifications) and receives
    rewards based on backtest performance metrics.
    
    State: Current parameters + recent reward history
    Action: Parameter modifications (discretized)
    Reward: Function of Sharpe, return, drawdown, robustness
    """
    
    def __init__(
        self,
        strategy_name: str,
        param_space: Dict[str, Any],
        backtester_func: Optional[callable] = None,
        max_steps: int = 20,
        reward_mode: str = 'sharpe_focused'
    ):
        """
        Initialize RL environment.
        
        Args:
            strategy_name: Strategy to optimize
            param_space: Parameter search space
            backtester_func: Backtest function (uses default if None)
            max_steps: Maximum steps per episode
            reward_mode: 'sharpe_focused', 'return_focused', or 'balanced'
        """
        self.strategy_name = strategy_name
        self.param_space = param_space
        self.max_steps = max_steps
        self.reward_mode = reward_mode
        
        # State tracking
        self.state: Optional[RLState] = None
        self.episode_step = 0
        self.best_params = None
        self.best_reward = -np.inf
        
        # Backtester
        if backtester_func is None:
            try:
                from meridian_v2_1_2.api import run_backtest
                self.backtester = run_backtest
            except ImportError:
                raise RuntimeError("No backtest function available")
        else:
            self.backtester = backtester_func
        
        # Action space: which parameter to modify and how
        self.action_space_size = len(param_space) * 3  # per param: increase, decrease, reset
        
        # History
        self.episode_history = []
    
    def reset(self) -> RLState:
        """
        Reset environment to start of episode.
        
        Returns:
            Initial state
        """
        # Initialize with random parameters from space
        initial_params = self._random_params()
        
        self.state = RLState(
            current_params=initial_params,
            recent_rewards=[],
            episode_step=0,
            best_reward_so_far=-np.inf
        )
        
        self.episode_step = 0
        self.episode_history = []
        
        return self.state
    
    def step(self, action: int) -> Tuple[RLState, float, bool, Dict[str, Any]]:
        """
        Take action and return next state, reward, done flag, and info.
        
        Args:
            action: Integer action (which param to modify and how)
        
        Returns:
            (next_state, reward, done, info)
        """
        # Decode action
        param_to_modify, modification_type = self._decode_action(action)
        
        # Apply modification
        new_params = self._modify_params(
            self.state.current_params,
            param_to_modify,
            modification_type
        )
        
        # Evaluate new parameters
        reward, metrics = self._evaluate_params(new_params)
        
        # Update state
        self.state.current_params = new_params
        self.state.recent_rewards.append(reward)
        if len(self.state.recent_rewards) > 5:
            self.state.recent_rewards = self.state.recent_rewards[-5:]
        
        self.state.episode_step = self.episode_step
        self.state.best_reward_so_far = max(self.state.best_reward_so_far, reward)
        
        # Track best overall
        if reward > self.best_reward:
            self.best_reward = reward
            self.best_params = copy.deepcopy(new_params)
        
        # Episode done?
        self.episode_step += 1
        done = self.episode_step >= self.max_steps
        
        # Info dict
        info = {
            'params': new_params,
            'metrics': metrics,
            'action': action,
            'param_modified': param_to_modify,
            'modification': modification_type
        }
        
        # Log history
        self.episode_history.append({
            'step': self.episode_step,
            'params': new_params,
            'reward': reward,
            'metrics': metrics
        })
        
        return self.state, reward, done, info
    
    def _random_params(self) -> Dict[str, Any]:
        """Generate random parameters from space"""
        params = {}
        for key, value_space in self.param_space.items():
            if isinstance(value_space, tuple):
                if isinstance(value_space[0], int):
                    params[key] = np.random.randint(value_space[0], value_space[1] + 1)
                else:
                    params[key] = np.random.uniform(value_space[0], value_space[1])
            elif isinstance(value_space, list):
                params[key] = np.random.choice(value_space)
        return params
    
    def _decode_action(self, action: int) -> Tuple[str, str]:
        """Decode action integer into (param_name, modification_type)"""
        n_params = len(self.param_space)
        param_idx = action // 3
        mod_type_idx = action % 3
        
        param_names = list(self.param_space.keys())
        param_name = param_names[param_idx % n_params]
        
        mod_types = ['increase', 'decrease', 'reset']
        modification = mod_types[mod_type_idx]
        
        return param_name, modification
    
    def _modify_params(
        self,
        params: Dict[str, Any],
        param_name: str,
        modification: str
    ) -> Dict[str, Any]:
        """Apply modification to parameter"""
        new_params = copy.deepcopy(params)
        value_space = self.param_space[param_name]
        
        if isinstance(value_space, tuple):
            current = params.get(param_name, (value_space[0] + value_space[1]) / 2)
            range_size = value_space[1] - value_space[0]
            
            if modification == 'increase':
                new_value = current + range_size * 0.1
            elif modification == 'decrease':
                new_value = current - range_size * 0.1
            else:  # reset
                new_value = np.random.uniform(value_space[0], value_space[1])
            
            # Clip to bounds
            new_value = np.clip(new_value, value_space[0], value_space[1])
            
            if isinstance(value_space[0], int):
                new_params[param_name] = int(round(new_value))
            else:
                new_params[param_name] = new_value
        
        elif isinstance(value_space, list):
            if modification == 'reset':
                new_params[param_name] = np.random.choice(value_space)
            else:
                # For categorical, just pick different option
                current_idx = value_space.index(params.get(param_name, value_space[0]))
                if modification == 'increase':
                    new_idx = min(current_idx + 1, len(value_space) - 1)
                else:
                    new_idx = max(current_idx - 1, 0)
                new_params[param_name] = value_space[new_idx]
        
        return new_params
    
    def _evaluate_params(self, params: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Evaluate parameters and return reward"""
        try:
            result = self.backtester(
                strategy_name=self.strategy_name,
                params=params
            )
            
            metrics = result.metrics if hasattr(result, 'metrics') else {}
            
            # Calculate reward based on mode
            reward = self._calculate_reward(metrics)
            
            return reward, metrics
            
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return -100.0, {}  # Large penalty for failed evaluation
    
    def _calculate_reward(self, metrics: Dict[str, float]) -> float:
        """Calculate reward from metrics"""
        sharpe = metrics.get('sharpe_ratio', 0)
        total_return = metrics.get('total_return', 0)
        max_dd = abs(metrics.get('max_drawdown', 0))
        
        if self.reward_mode == 'sharpe_focused':
            reward = sharpe * 20 + total_return * 10
        elif self.reward_mode == 'return_focused':
            reward = total_return * 50 + sharpe * 5
        else:  # balanced
            reward = sharpe * 15 + total_return * 20
        
        # Drawdown penalty
        if max_dd > 0.15:
            reward -= (max_dd - 0.15) * 100
        
        return float(reward)
    
    def get_best_params(self) -> Tuple[Dict[str, Any], float]:
        """Get best parameters found so far"""
        return self.best_params, self.best_reward

