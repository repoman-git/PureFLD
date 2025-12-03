"""
AI Research Agents Dashboard

Multi-agent analysis system with specialized AI agents.
Each agent provides unique perspective on strategy performance.
"""

import streamlit as st
import pandas as pd

from meridian_v2_1_2.agents import (
    ResearchOrchestrator,
    CycleAnalysisAgent,
    FLDInspectorAgent,
    BacktestCriticAgent,
    RiskProfilerAgent,
    ParameterScientistAgent,
    StrategyGeneratorAgent,
    DocumentationAgent,
    COTAnalysisAgent,
    MarketRegimeAgent,
    PerformanceAuditorAgent
)
from meridian_v2_1_2.storage import load_all_runs, load_run_by_id

st.set_page_config(
    page_title="Meridian - AI Research Agents",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Research Agents")
st.markdown("*Multi-agent analysis system for comprehensive strategy evaluation*")
st.markdown("---")

# Initialize agents
ALL_AGENTS = [
    CycleAnalysisAgent(),
    FLDInspectorAgent(),
    BacktestCriticAgent(),
    RiskProfilerAgent(),
    ParameterScientistAgent(),
    StrategyGeneratorAgent(),
    DocumentationAgent(),
    COTAnalysisAgent(),
    MarketRegimeAgent(),
    PerformanceAuditorAgent()
]

# ═══════════════════════════════════════════════════════════════════
# AGENT SELECTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("🎯 Select Agents")

with st.expander("ℹ️ About Multi-Agent Research", expanded=False):
    st.markdown("""
    ### How It Works:
    
    Each AI agent specializes in a specific aspect of strategy analysis:
    - **Cycle Analyst:** FLD mechanics and cycle tuning
    - **FLD Inspector:** Signal quality and timing
    - **Backtest Critic:** Statistical validity
    - **Risk Profiler:** Drawdown and tail risk
    - **Parameter Scientist:** Optimization opportunities
    - **Strategy Generator:** New variations and ideas
    - **Documentation Agent:** Report generation
    
    Agents run independently and orchestrator aggregates their insights.
    
    **Current:** Rule-based heuristics  
    **Future:** Can connect to GPT-4/Claude for enhanced analysis
    """)

# Multi-select for agents
agent_names = [agent.name for agent in ALL_AGENTS]
selected_agent_names = st.multiselect(
    "Choose agents to activate",
    agent_names,
    default=agent_names[:5]  # Select first 5 by default
)

if not selected_agent_names:
    st.warning("⚠️  Select at least one agent")
    st.stop()

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# RUN SELECTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("📊 Select Backtest Run")

runs = load_all_runs()

if not runs:
    st.info("📭 No backtest runs found. Run a backtest first.")
    st.stop()

# Create run selection options
run_options = []
for run in runs[:30]:
    strategy = run.get('strategy_name', 'Unknown')
    run_id = run.get('run_id', 'N/A')[:8]
    timestamp = run.get('timestamp', '')[:16]
    sharpe = run.get('metrics', {}).get('sharpe_ratio', 0)
    run_options.append(f"{run_id} | {strategy} | {timestamp} | Sharpe: {sharpe:.2f}")

selected_option = st.selectbox("Select run to analyze", run_options)

if not selected_option:
    st.stop()

# Load full run data
selected_run_id = selected_option.split(' | ')[0]
full_run_id = None
for run in runs:
    if run.get('run_id', '').startswith(selected_run_id):
        full_run_id = run.get('run_id')
        break

run_data = load_run_by_id(full_run_id)

if not run_data:
    st.error("Failed to load run data")
    st.stop()

st.markdown("---")

# ═══════================================================================
# RUN RESEARCH CYCLE
# ═══════════════════════════════════════════════════════════════════

st.subheader("🚀 Run Multi-Agent Analysis")

if st.button("🤖 Activate AI Agents", type="primary", use_container_width=True):
    with st.spinner(f"Running {len(selected_agent_names)} AI agents..."):
        try:
            # Create orchestrator with selected agents
            selected_agents = [a for a in ALL_AGENTS if a.name in selected_agent_names]
            orchestrator = ResearchOrchestrator(selected_agents)
            
            # Run research cycle
            report = orchestrator.run_research_cycle(run_data)
            
            # Store in session
            st.session_state.research_report = report
            
            st.success(f"✅ Analysis complete! Generated {len(report.all_insights)} insights")
            
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════════

if hasattr(st.session_state, 'research_report'):
    report = st.session_state.research_report
    
    st.markdown("---")
    st.subheader("📋 Research Report")
    
    # Executive Summary
    st.markdown("### 📊 Executive Summary")
    st.info(report.executive_summary)
    
    st.markdown("---")
    
    # Critical Issues
    if report.critical_issues:
        st.markdown("### ⚠️  Critical Issues")
        for issue in report.critical_issues:
            icon = '🔴' if issue.priority == 'critical' else '🟡'
            st.error(f"{icon} **[{issue.agent_name}]** {issue.title}\n\n{issue.content}")
    
    st.markdown("---")
    
    # Agent-by-Agent Analysis
    st.markdown("### 🤖 Agent Reports")
    
    for agent_name, analysis in report.agent_insights.items():
        with st.expander(f"🔍 {agent_name}", expanded=False):
            st.markdown(f"**Summary:** {analysis.get('summary', 'N/A')}")
            
            insights = analysis.get('insights', [])
            if insights:
                st.markdown("**Insights:**")
                for insight in insights:
                    priority_icon = {
                        'critical': '🔴',
                        'high': '🟡',
                        'medium': '🔵',
                        'low': '⚪'
                    }.get(insight.priority, '•')
                    
                    st.markdown(f"{priority_icon} **{insight.title}**")
                    st.caption(insight.content)
            
            recs = analysis.get('recommendations', [])
            if recs:
                st.markdown("**Recommendations:**")
                for rec in recs:
                    st.markdown(f"✅ {rec}")
    
    st.markdown("---")
    
    # Consolidated Recommendations
    st.markdown("### 💡 All Recommendations")
    for i, rec in enumerate(report.recommendations, 1):
        st.markdown(f"{i}. {rec}")
    
    # Export
    st.markdown("---")
    st.subheader("📤 Export Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as Markdown"):
            from meridian_v2_1_2.agents.orchestrator import ResearchOrchestrator
            # Create temp orchestrator for export
            temp_orch = ResearchOrchestrator(ALL_AGENTS)
            markdown_report = temp_orch.export_report_to_markdown(report)
            
            st.download_button(
                label="Download Report",
                data=markdown_report,
                file_name=f"research_report_{report.report_id}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("📓 Open in Notebook"):
            st.info("Generate research notebook with full analysis (Phase 4B integration)")

# Footer
st.markdown("---")
st.caption("Phase 7 | Multi-AI Research Agent System")
st.caption("🔮 Future: Connect to GPT-4/Claude for enhanced analysis")

