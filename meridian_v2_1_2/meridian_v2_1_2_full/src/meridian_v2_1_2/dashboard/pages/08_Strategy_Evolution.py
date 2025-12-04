"""
Strategy Evolution Dashboard

AI-Assisted genetic algorithm for strategy optimization.
Evolve parameters using Darwinian selection + mutation + crossover.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Phase 6 modules
from meridian_v2_1_2.evolution import (
    evolve_strategy,
    FLD_PARAM_SPACE,
    COT_PARAM_SPACE,
    GENERIC_PARAM_SPACE,
    EvolutionResult,
    export_best_to_dict
)
from meridian_v2_1_2.storage.evolution_registry import (
    save_evolution_run,
    load_all_evolution_runs,
    get_evolution_stats,
    get_best_evolved_params
)
from meridian_v2_1_2.dashboard.components.evolution_viz import (
    plot_fitness_curve,
    plot_population_scatter,
    plot_diversity_metric
)
from meridian_v2_1_2.ai import ai_feedback

st.set_page_config(
    page_title="Meridian - Strategy Evolution",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 Strategy Evolution Engine")
st.markdown("*AI-Assisted Genetic Algorithm for Strategy Optimization*")
st.markdown("---")

# Initialize session state
if 'evolution_running' not in st.session_state:
    st.session_state.evolution_running = False
if 'evolution_result' not in st.session_state:
    st.session_state.evolution_result = None

# ═══════════════════════════════════════════════════════════════════
# EVOLUTION HISTORY
# ═══════════════════════════════════════════════════════════════════

stats = get_evolution_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Runs", stats.get('total_runs', 0))
with col2:
    st.metric("Generations", stats.get('total_generations', 0))
with col3:
    st.metric("Strategies", len(stats.get('strategies', {})))
with col4:
    st.metric("Avg Gens/Run", f"{stats.get('avg_generations', 0):.1f}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# EVOLUTION CONTROLS
# ═══════════════════════════════════════════════════════════════════

st.subheader("⚙️ Evolution Settings")

with st.expander("ℹ️ How Evolution Works", expanded=False):
    st.markdown("""
    ### Genetic Algorithm Process:
    
    1. **Initialize:** Create random population of parameter sets
    2. **Evaluate:** Run backtest + score each candidate
    3. **Select:** Choose best performers as parents (tournament selection)
    4. **Crossover:** Combine parameters from two parents
    5. **Mutate:** Randomly tweak parameters
    6. **Repeat:** Create new generation, keep best (elitism)
    
    ### Fitness Function:
    - **Sharpe Ratio** (primary, 10x weight)
    - **Total Return** (20x weight)
    - **Drawdown Penalty** (heavy for >15%)
    - **Optional:** Monte Carlo robustness bonus
    
    ### Result:
    Automatically discovers optimal parameter combinations through evolutionary search.
    """)

col1, col2, col3 = st.columns(3)

with col1:
    strategy_name = st.selectbox(
        "Strategy to Evolve",
        ["FLD", "COT", "GENERIC"],
        help="Select which strategy to optimize"
    )

with col2:
    population_size = st.number_input(
        "Population Size",
        min_value=10,
        max_value=50,
        value=20,
        step=5,
        help="Number of candidates per generation"
    )

with col3:
    num_generations = st.number_input(
        "Generations",
        min_value=5,
        max_value=50,
        value=10,
        step=5,
        help="Number of evolution cycles"
    )

col1, col2, col3 = st.columns(3)

with col1:
    mutation_rate = st.slider(
        "Mutation Rate",
        min_value=0.05,
        max_value=0.50,
        value=0.15,
        step=0.05,
        help="Probability of random parameter changes"
    )

with col2:
    crossover_rate = st.slider(
        "Crossover Rate",
        min_value=0.30,
        max_value=0.90,
        value=0.50,
        step=0.10,
        help="Probability of combining parent parameters"
    )

with col3:
    elite_size = st.number_input(
        "Elite Size",
        min_value=1,
        max_value=5,
        value=2,
        help="Top N candidates preserved each generation"
    )

# Parameter space display
st.markdown("### 📐 Parameter Space")

param_spaces = {
    'FLD': FLD_PARAM_SPACE,
    'COT': COT_PARAM_SPACE,
    'GENERIC': GENERIC_PARAM_SPACE
}

selected_space = param_spaces[strategy_name]

# Display as table
space_data = []
for param, bounds in selected_space.items():
    if isinstance(bounds, tuple):
        space_data.append({
            'Parameter': param,
            'Type': 'Numeric',
            'Min': bounds[0],
            'Max': bounds[1],
            'Options': '-'
        })
    else:
        space_data.append({
            'Parameter': param,
            'Type': 'Categorical',
            'Min': '-',
            'Max': '-',
            'Options': ', '.join(str(x) for x in bounds)
        })

st.dataframe(pd.DataFrame(space_data), use_container_width=True, hide_index=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# START EVOLUTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("🚀 Run Evolution")

col1, col2 = st.columns([2, 1])

with col1:
    run_evolution = st.button(
        "🧬 Start Evolution",
        type="primary",
        disabled=st.session_state.evolution_running,
        use_container_width=True
    )

with col2:
    use_mock = st.checkbox("Use Mock Backtester (Fast)", value=True, help="Use mock for testing, uncheck for real backtests")

if run_evolution:
    st.session_state.evolution_running = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create callback for progress updates
    def progress_callback(gen, candidate_idx, population, candidate):
        progress = (gen + (candidate_idx / population)) / num_generations
        progress_bar.progress(progress)
        status_text.text(f"Gen {gen+1}/{num_generations} | Candidate {candidate_idx+1}/{population} | Fitness: {candidate.fitness:.2f}")
    
    with st.spinner("Evolution in progress..."):
        try:
            # Mock backtester for testing
            if use_mock:
                def mock_backtester(strategy_name, params, **kwargs):
                    class MockResult:
                        def __init__(self):
                            self.metrics = {
                                'sharpe_ratio': abs(np.random.normal(1.0, 0.3)),
                                'total_return': abs(np.random.normal(0.15, 0.10)),
                                'max_drawdown': -abs(np.random.normal(0.12, 0.05)),
                                'win_rate': abs(np.random.normal(0.55, 0.10)),
                                'num_trades': int(np.random.normal(50, 10))
                            }
                            self.equity_curve = []
                    
                    import numpy as np
                    return MockResult()
                
                backtester = mock_backtester
            else:
                from meridian_v2_1_2.api import run_backtest
                backtester = run_backtest
            
            # Run evolution
            result = evolve_strategy(
                strategy_name=strategy_name,
                param_space=selected_space,
                population=population_size,
                generations=num_generations,
                mutation_rate=mutation_rate,
                crossover_rate=crossover_rate,
                elite_size=elite_size,
                backtester_func=backtester,
                callback=progress_callback
            )
            
            # Save to registry
            evolution_dict = export_best_to_dict(result)
            save_evolution_run(evolution_dict)
            
            # Store in session
            st.session_state.evolution_result = evolution_dict
            st.session_state.evolution_running = False
            
            progress_bar.progress(1.0)
            status_text.text("✅ Evolution complete!")
            st.success(f"🏆 Best Fitness: {result.best_candidate.fitness:.2f}")
            st.balloons()
            
        except Exception as e:
            st.error(f"Evolution failed: {e}")
            st.session_state.evolution_running = False

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# EVOLUTION RESULTS
# ═══════════════════════════════════════════════════════════════════

if st.session_state.evolution_result:
    result = st.session_state.evolution_result
    
    st.subheader("📊 Evolution Results")
    
    best = result['best_candidate']
    history = result['history']
    
    # Display best candidate
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🏆 Best Candidate")
        st.metric("Fitness", f"{best['fitness']:.2f}")
        st.metric("Generation", f"{best.get('generation', 0)}")
        
        metrics = best.get('metrics', {})
        st.metric("Sharpe", f"{metrics.get('sharpe_ratio', 0):.2f}")
        st.metric("Return", f"{metrics.get('total_return', 0):.1%}")
        st.metric("Max DD", f"{metrics.get('max_drawdown', 0):.1%}")
    
    with col2:
        st.markdown("### ⚙️ Best Parameters")
        st.json(best['params'])
    
    # Visualizations
    st.markdown("### 📈 Fitness Evolution")
    
    if history:
        fig = plot_fitness_curve(history)
        st.plotly_chart(fig, use_container_width=True)
        
        # Diversity
        fig2 = plot_diversity_metric(history)
        st.plotly_chart(fig2, use_container_width=True)
    
    # AI Feedback
    st.markdown("### 🤖 AI Coach Feedback")
    
    feedback = ai_feedback(best.get('metrics', {}), mc_stats=best.get('mc_stats', {}))
    
    for fb in feedback:
        if '🔴' in fb:
            st.error(fb)
        elif '🟡' in fb:
            st.warning(fb)
        else:
            st.info(fb)
    
    # Export options
    st.markdown("---")
    st.subheader("📤 Export Best Strategy")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to Registry"):
            st.success("Already saved to evolution registry!")
    
    with col2:
        if st.button("📓 Export to Notebook"):
            st.info("Generate notebook from best params (Phase 4B integration)")
            # TODO: Integrate with notebook generation
    
    with col3:
        if st.button("📊 Run Robustness Test"):
            st.info("Navigate to Robustness page to analyze this candidate")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# EVOLUTION HISTORY
# ═══════════════════════════════════════════════════════════════════

st.subheader("📜 Evolution History")

all_runs = load_all_evolution_runs()

if all_runs:
    runs_data = []
    for run in all_runs[:20]:  # Show last 20
        best = run.get('best_candidate', {})
        runs_data.append({
            'Evolution ID': run.get('evolution_id', '')[-12:],
            'Strategy': run.get('strategy_name', 'Unknown'),
            'Gens': run.get('generations', 0),
            'Pop Size': run.get('population_size', 0),
            'Best Fitness': f"{best.get('fitness', 0):.2f}",
            'Best Sharpe': f"{best.get('metrics', {}).get('sharpe_ratio', 0):.2f}",
            'Timestamp': run.get('timestamp', '')[:16]
        })
    
    df = pd.DataFrame(runs_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Best evolved parameters
    st.markdown("### 🏆 Hall of Fame - Best Evolved Parameters")
    
    selected_strategy_hof = st.selectbox("View best params for strategy", ["FLD", "COT", "GENERIC"])
    best_params = get_best_evolved_params(selected_strategy_hof, n=5)
    
    if best_params:
        for i, param_set in enumerate(best_params, 1):
            with st.expander(f"#{i} - Fitness: {param_set['fitness']:.2f} | {param_set.get('timestamp', '')[:16]}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.json(param_set['params'])
                with col2:
                    metrics = param_set.get('metrics', {})
                    st.metric("Sharpe", f"{metrics.get('sharpe_ratio', 0):.2f}")
                    st.metric("Return", f"{metrics.get('total_return', 0):.1%}")
                    st.metric("Max DD", f"{metrics.get('max_drawdown', 0):.1%}")
                
                if st.button(f"📋 Copy Params #{i}", key=f"copy_{i}"):
                    st.code(str(param_set['params']))
    else:
        st.info(f"No evolved parameters for {selected_strategy_hof} yet. Run an evolution!")

else:
    st.info("No evolution runs yet. Start your first evolution above!")

# Footer
st.markdown("---")
st.caption(f"Phase 6 | Strategy Evolution Engine")
st.caption("💡 Tip: Start with 20 population, 10 generations for quick experiments")


