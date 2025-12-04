"""
RL Training Loop

Train RL agent to optimize strategy parameters through interaction.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RLTrainingResult:
    """Results from RL training run"""
    training_id: str
    strategy_name: str
    episodes: int
    best_params: Dict[str, Any]
    best_reward: float
    reward_history: List[float]  # Best reward per episode
    episode_summaries: List[Dict[str, Any]]
    final_epsilon: float
    total_steps: int
    timestamp: str


def train_rl_agent(
    env,
    agent,
    episodes: int = 50,
    verbose: bool = True,
    callback: Optional[Callable] = None
) -> RLTrainingResult:
    """
    Train RL agent to optimize strategy parameters.
    
    Agent learns through trial and error which parameter modifications
    lead to better backtest performance.
    
    Args:
        env: BacktestEnv instance
        agent: RLStrategyAgent instance
        episodes: Number of training episodes
        verbose: Print progress
        callback: Progress callback function(episode, step, reward)
    
    Returns:
        RLTrainingResult: Complete training results
    
    Example:
        >>> from meridian_v2_1_2.rl import BacktestEnv, RLStrategyAgent, train_rl_agent
        >>> from meridian_v2_1_2.evolution import FLD_PARAM_SPACE
        >>> 
        >>> env = BacktestEnv('FLD', FLD_PARAM_SPACE)
        >>> agent = RLStrategyAgent(env.action_space_size)
        >>> result = train_rl_agent(env, agent, episodes=20)
        >>> 
        >>> print(f"Best reward: {result.best_reward:.2f}")
        >>> print(f"Best params: {result.best_params}")
    """
    
    training_id = f"rl_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if verbose:
        print(f"🎓 Starting RL Training: {training_id}")
        print(f"   Strategy: {env.strategy_name}")
        print(f"   Episodes: {episodes}")
        print(f"   Initial epsilon: {agent.epsilon:.3f}")
    
    reward_history = []
    episode_summaries = []
    total_steps = 0
    best_overall_reward = -np.inf
    best_overall_params = None
    
    # Training loop
    for episode in range(episodes):
        state = env.reset()
        episode_reward = 0
        episode_steps = 0
        done = False
        
        while not done:
            # Select action
            action = agent.select_action(state, training=True)
            
            # Take step
            next_state, reward, done, info = env.step(action)
            
            # Update agent
            agent.update(state, action, reward, next_state, done)
            
            episode_reward += reward
            episode_steps += 1
            total_steps += 1
            
            state = next_state
            
            # Callback for UI updates
            if callback:
                callback(episode, episode_steps, reward)
        
        # Episode complete
        agent.decay_epsilon()
        agent.episodes_trained += 1
        
        # Track best from this episode
        best_params, best_reward = env.get_best_params()
        
        if best_reward > best_overall_reward:
            best_overall_reward = best_reward
            best_overall_params = best_params
        
        reward_history.append(best_reward)
        
        # Episode summary
        episode_summaries.append({
            'episode': episode,
            'episode_reward': episode_reward,
            'episode_steps': episode_steps,
            'best_params': best_params,
            'best_reward': best_reward,
            'epsilon': agent.epsilon
        })
        
        if verbose:
            print(f"   Episode {episode+1}/{episodes} | "
                  f"Reward: {episode_reward:.2f} | "
                  f"Best: {best_reward:.2f} | "
                  f"ε: {agent.epsilon:.3f}")
    
    if verbose:
        print(f"\n🏆 Training Complete!")
        print(f"   Best Reward: {best_overall_reward:.2f}")
        print(f"   Total Steps: {total_steps}")
        print(f"   Q-table Size: {len(agent.q_table)}")
    
    return RLTrainingResult(
        training_id=training_id,
        strategy_name=env.strategy_name,
        episodes=episodes,
        best_params=best_overall_params,
        best_reward=best_overall_reward,
        reward_history=reward_history,
        episode_summaries=episode_summaries,
        final_epsilon=agent.epsilon,
        total_steps=total_steps,
        timestamp=datetime.now().isoformat()
    )


def train_with_curriculum(
    env,
    agent,
    curriculum: List[Dict[str, Any]],
    episodes_per_stage: int = 20
) -> RLTrainingResult:
    """
    Train agent using curriculum learning.
    
    Starts with easier objectives, progressively increases difficulty.
    
    Args:
        env: Environment
        agent: Agent
        curriculum: List of stage configs (e.g., different reward modes)
        episodes_per_stage: Episodes per curriculum stage
    
    Returns:
        RLTrainingResult: Combined training results
    """
    
    print(f"🎓 Curriculum Learning: {len(curriculum)} stages")
    
    all_summaries = []
    all_rewards = []
    total_episodes = 0
    
    for stage_idx, stage_config in enumerate(curriculum):
        print(f"\n📚 Stage {stage_idx + 1}/{len(curriculum)}: {stage_config.get('name', 'Unnamed')}")
        
        # Update environment config
        if 'reward_mode' in stage_config:
            env.reward_mode = stage_config['reward_mode']
        if 'max_steps' in stage_config:
            env.max_steps = stage_config['max_steps']
        
        # Train for this stage
        result = train_rl_agent(env, agent, episodes=episodes_per_stage, verbose=True)
        
        all_summaries.extend(result.episode_summaries)
        all_rewards.extend(result.reward_history)
        total_episodes += episodes_per_stage
    
    # Return combined results
    return RLTrainingResult(
        training_id=f"curriculum_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        strategy_name=env.strategy_name,
        episodes=total_episodes,
        best_params=env.best_params,
        best_reward=env.best_reward,
        reward_history=all_rewards,
        episode_summaries=all_summaries,
        final_epsilon=agent.epsilon,
        total_steps=sum(len(env.episode_history) for s in all_summaries),
        timestamp=datetime.now().isoformat()
    )


