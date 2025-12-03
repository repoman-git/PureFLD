"""
Reinforcement Learning Agent

Q-learning agent for strategy parameter optimization.
Includes epsilon-greedy exploration and optional deep RL scaffolding.
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from collections import defaultdict
import pickle
from pathlib import Path
from .rl_environment import RLState


class RLStrategyAgent:
    """
    Q-learning agent for strategy optimization.
    
    Uses tabular Q-learning with discretized states.
    Includes placeholder for deep RL (MLP) future expansion.
    """
    
    def __init__(
        self,
        action_space_size: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.2,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        use_deep_rl: bool = False
    ):
        """
        Initialize RL agent.
        
        Args:
            action_space_size: Number of possible actions
            learning_rate: Alpha for Q-learning update
            discount_factor: Gamma for future reward discounting
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon value
            use_deep_rl: Use neural network (placeholder, not trained yet)
        """
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.use_deep_rl = use_deep_rl
        
        # Q-table: state_hash -> action -> Q-value
        self.q_table = defaultdict(lambda: np.zeros(action_space_size))
        
        # Deep RL placeholder (MLP model - not trained)
        self.model = None
        if use_deep_rl:
            self._init_neural_network()
        
        # Statistics
        self.total_updates = 0
        self.episodes_trained = 0
    
    def select_action(self, state: Any, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode (affects exploration)
        
        Returns:
            Action integer
        """
        # Epsilon-greedy exploration
        if training and np.random.random() < self.epsilon:
            # Explore: random action
            return np.random.randint(0, self.action_space_size)
        else:
            # Exploit: best known action
            state_hash = self._hash_state(state)
            q_values = self.q_table[state_hash]
            
            # Handle ties randomly
            max_q = np.max(q_values)
            best_actions = np.where(q_values == max_q)[0]
            return np.random.choice(best_actions)
    
    def update(
        self,
        state: Any,
        action: int,
        reward: float,
        next_state: Any,
        done: bool
    ):
        """
        Update Q-values using Q-learning update rule.
        
        Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Resulting state
            done: Whether episode ended
        """
        state_hash = self._hash_state(state)
        next_state_hash = self._hash_state(next_state)
        
        # Current Q-value
        current_q = self.q_table[state_hash][action]
        
        # Max Q-value for next state
        if done:
            next_max_q = 0
        else:
            next_max_q = np.max(self.q_table[next_state_hash])
        
        # Q-learning update
        td_target = reward + self.discount_factor * next_max_q
        td_error = td_target - current_q
        new_q = current_q + self.learning_rate * td_error
        
        # Update Q-table
        self.q_table[state_hash][action] = new_q
        
        self.total_updates += 1
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def get_best_action(self, state: Any) -> Tuple[int, float]:
        """
        Get best action for state (pure exploitation).
        
        Returns:
            (best_action, q_value)
        """
        state_hash = self._hash_state(state)
        q_values = self.q_table[state_hash]
        best_action = np.argmax(q_values)
        return int(best_action), float(q_values[best_action])
    
    def save(self, path: Path):
        """Save agent to disk"""
        state = {
            'q_table': dict(self.q_table),
            'epsilon': self.epsilon,
            'total_updates': self.total_updates,
            'episodes_trained': self.episodes_trained,
            'action_space_size': self.action_space_size
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state, f)
    
    def load(self, path: Path):
        """Load agent from disk"""
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.q_table = defaultdict(lambda: np.zeros(self.action_space_size), state['q_table'])
        self.epsilon = state['epsilon']
        self.total_updates = state['total_updates']
        self.episodes_trained = state['episodes_trained']
    
    def _hash_state(self, state: Any) -> str:
        """
        Convert state to hashable string for Q-table lookup.
        
        Discretizes continuous parameters for tabular RL.
        """
        if isinstance(state, RLState):
            # Discretize parameters to create state hash
            param_str = []
            for key, value in sorted(state.current_params.items()):
                if isinstance(value, bool):
                    param_str.append(f"{key}:{int(value)}")
                elif isinstance(value, float):
                    # Discretize to 10 bins
                    discretized = int(value * 10) / 10
                    param_str.append(f"{key}:{discretized:.1f}")
                else:
                    param_str.append(f"{key}:{value}")
            
            return '|'.join(param_str)
        else:
            return str(state)
    
    def _init_neural_network(self):
        """
        Initialize neural network for deep RL (placeholder).
        
        This is scaffolding for future deep RL implementation.
        Not trained in current phase.
        """
        # Placeholder: Would use PyTorch or TensorFlow
        # For now, just document the architecture
        self.model = {
            'type': 'MLP',
            'layers': [64, 64],
            'activation': 'relu',
            'output': self.action_space_size,
            'trained': False,
            'note': 'Placeholder for future deep RL - not yet implemented'
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'q_table_size': len(self.q_table),
            'total_updates': self.total_updates,
            'episodes_trained': self.episodes_trained,
            'current_epsilon': self.epsilon,
            'using_deep_rl': self.use_deep_rl and self.model is not None
        }

