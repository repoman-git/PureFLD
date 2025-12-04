"""
RL Trainer Dashboard

Train reinforcement learning agents to optimize strategy parameters.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from meridian_v2_1_2.rl import BacktestEnv, RLStrategyAgent, train_rl_agent
from meridian_v2_1_2.evolution import FLD_PARAM_SPACE, COT_PARAM_SPACE, get_param_space
from meridian_v2_1_2.storage.evolution_registry import save_evolution_run

st.set_page_config(
    page_title="Meridian - RL Trainer",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Reinforcement Learning Trainer")
st.markdown("*Train RL agent to optimize strategy parameters through interaction*")
st.markdown("---")

# Initialize session state
if 'rl_training' not in st.session_state:
    st.session_state.rl_training = False
if 'rl_result' not in st.session_state:
    st.session_state.rl_result = None

# ═══════════════════════════════════════════════════════════════════
# RL TRAINING CONTROLS
# ═══════════════════════════════════════════════════════════════════

st.subheader("⚙️ RL Training Settings")

with st.expander("ℹ️ How RL Training Works", expanded=False):
    st.markdown("""
    ### Reinforcement Learning Process:
    
    1. **Environment:** Strategy backtest with parameter space
    2. **Agent:** Q-learning agent that learns optimal parameter modifications
    3. **State:** Current parameters + recent reward history
    4. **Action:** Modify a parameter (increase/decrease/reset)
    5. **Reward:** Based on backtest performance (Sharpe + Return - Drawdown penalty)
    6. **Learning:** Agent updates Q-table based on rewards
    
    ### Why RL?
    - Discovers **non-obvious** parameter interactions
    - **Adaptive** to different market conditions
    - **Continuous learning** from experience
    - Complements genetic algorithms (Phase 6)
    
    ### Difference from Evolution:
    - **Evolution (Phase 6):** Population-based, parallel search
    - **RL (Phase 7):** Sequential learning, exploitation of learned policies
    - **Best:** Use both! Evolution for exploration, RL for refinement
    """)

col1, col2, col3 = st.columns(3)

with col1:
    strategy_name = st.selectbox("Strategy", ["FLD", "COT", "GENERIC"])

with col2:
    episodes = st.number_input("Episodes", min_value=10, max_value=200, value=50, step=10)

with col3:
    max_steps = st.number_input("Max Steps/Episode", min_value=10, max_value=50, value=20, step=5)

col1, col2, col3 = st.columns(3)

with col1:
    learning_rate = st.slider("Learning Rate", 0.01, 0.50, 0.10, 0.05)

with col2:
    epsilon = st.slider("Exploration (ε)", 0.05, 0.50, 0.20, 0.05)

with col3:
    discount = st.slider("Discount (γ)", 0.80, 0.99, 0.95, 0.01)

reward_mode = st.selectbox(
    "Reward Mode",
    ["sharpe_focused", "return_focused", "balanced"],
    help="What should the agent optimize for?"
)

use_mock = st.checkbox("Use Mock Backtester (Fast)", value=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# START TRAINING
# ═══════════════════════════════════════════════════════════════════

st.subheader("🚀 Start RL Training")

if st.button("🎓 Train RL Agent", type="primary", disabled=st.session_state.rl_training):
    st.session_state.rl_training = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    reward_chart_placeholder = st.empty()
    
    with st.spinner("Training RL agent..."):
        try:
            # Get parameter space
            param_space = get_param_space(strategy_name)
            
            # Create environment
            if use_mock:
                def mock_backtest(strategy_name, params, **kwargs):
                    class MockResult:
                        def __init__(self):
                            import numpy as np
                            self.metrics = {
                                'sharpe_ratio': abs(np.random.normal(1.0, 0.3)),
                                'total_return': abs(np.random.normal(0.15, 0.10)),
                                'max_drawdown': -abs(np.random.normal(0.12, 0.05)),
                                'win_rate': abs(np.random.normal(0.55, 0.10)),
                            }
                    return MockResult()
                
                backtester = mock_backtest
            else:
                from meridian_v2_1_2.api import run_backtest
                backtester = run_backtest
            
            env = BacktestEnv(
                strategy_name=strategy_name,
                param_space=param_space,
                backtester_func=backtester,
                max_steps=max_steps,
                reward_mode=reward_mode
            )
            
            # Create agent
            agent = RLStrategyAgent(
                action_space_size=env.action_space_size,
                learning_rate=learning_rate,
                epsilon=epsilon,
                discount_factor=discount
            )
            
            # Callback for progress
            episode_rewards = []
            
            def progress_callback(episode, step, reward):
                progress = episode / episodes
                progress_bar.progress(progress)
                status_text.text(f"Episode {episode+1}/{episodes} | Step {step} | Reward: {reward:.2f}")
            
            # Train
            result = train_rl_agent(env, agent, episodes=episodes, callback=progress_callback)
            
            # Store result
            st.session_state.rl_result = result
            st.session_state.rl_training = False
            
            progress_bar.progress(1.0)
            status_text.text("✅ Training complete!")
            
            st.success(f"🏆 Best Reward: {result.best_reward:.2f}")
            st.balloons()
            
        except Exception as e:
            st.error(f"Training failed: {e}")
            st.session_state.rl_training = False

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════════

if st.session_state.rl_result:
    result = st.session_state.rl_result
    
    st.subheader("📊 RL Training Results")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Best Reward", f"{result.best_reward:.2f}")
    with col2:
        st.metric("Episodes", result.episodes)
    with col3:
        st.metric("Total Steps", result.total_steps)
    with col4:
        st.metric("Final ε", f"{result.final_epsilon:.3f}")
    
    # Best parameters
    st.markdown("### 🏆 Best Parameters Found")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.json(result.best_params)
    
    with col2:
        st.markdown("**Actions:**")
        if st.button("📋 Copy Parameters"):
            st.code(str(result.best_params))
        if st.button("📊 Run Robustness Test"):
            st.info("Navigate to Robustness page with these params")
        if st.button("📓 Export to Notebook"):
            st.info("Generate notebook with optimized parameters")
    
    # Reward history
    st.markdown("### 📈 Learning Curve")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=result.reward_history,
        mode='lines+markers',
        name='Best Reward per Episode',
        line=dict(color='green', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="RL Agent Learning Progress",
        xaxis_title="Episode",
        yaxis_title="Best Reward",
        hovermode='x',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Episode summaries
    st.markdown("### 📋 Episode History")
    
    episode_data = []
    for ep in result.episode_summaries[-10:]:  # Last 10 episodes
        episode_data.append({
            'Episode': ep['episode'] + 1,
            'Reward': f"{ep['episode_reward']:.2f}",
            'Best': f"{ep['best_reward']:.2f}",
            'Steps': ep['episode_steps'],
            'Epsilon': f"{ep['epsilon']:.3f}"
        })
    
    if episode_data:
        st.dataframe(pd.DataFrame(episode_data), use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("Phase 7 | Reinforcement Learning Engine")
st.caption("💡 Tip: Start with high epsilon (0.3) for exploration, decay naturally")


