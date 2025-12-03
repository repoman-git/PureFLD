"""
AI Audit Engine Dashboard

Multi-AI verification and strategy audit system.
Prevents hallucinations, ensures transparency, provides regulatory safety.
"""

import streamlit as st
import pandas as pd

from meridian_v2_1_2.audit_engine import (
    AuditOrchestrator,
    build_audit_report,
    AuditReportFormat,
    get_model_profile
)
from meridian_v2_1_2.storage import load_all_runs, load_run_by_id
from meridian_v2_1_2.ai.ai_config_manager import load_ai_config

st.set_page_config(
    page_title="Meridian - AI Audit Engine",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI Audit & Verification Engine")
st.markdown("*Multi-AI cross-validation for strategy verification*")
st.markdown("---")

# Load AI config
ai_config = load_ai_config()
enabled_models = [
    name for name, config in ai_config.get('providers', {}).items()
    if config.get('enabled', False)
]

# ═══════════════════════════════════════════════════════════════════
# AUDIT CONTROLS
# ═══════════════════════════════════════════════════════════════════

st.subheader("⚙️ Audit Configuration")

with st.expander("ℹ️ About Multi-AI Audit System", expanded=False):
    st.markdown("""
    ### The Audit Engine:
    
    **Purpose:** Prevent hallucinations, ensure transparency, provide regulatory safety
    
    **3-Stage Process:**
    
    1. **Stage 1: Neutral Diagnostic**
       - Objective assessment
       - Strengths, weaknesses, gaps
       - Risk identification
       - Uncertainty labeling (FACT/INTERPRETATION/SPECULATION/LIMITATION)
    
    2. **Stage 2: Adversarial Stress Test**
       - Challenge assumptions aggressively
       - Find contradictions
       - Identify failure modes
       - Uncover hidden risks
    
    3. **Stage 3: Cross-Model Reconciliation**
       - Compare multiple AI audits
       - Find consensus
       - Identify disagreements
       - Calculate confidence score
    
    **HonestAI Protocol:**
    - No hallucinations allowed
    - Explicit uncertainty labeling
    - Clear limitations stated
    - Retail-safe explanations
    """)

col1, col2, col3 = st.columns(3)

with col1:
    if enabled_models:
        primary_model = st.selectbox(
            "Primary AI Model",
            enabled_models + ['claude', 'gemini', 'grok', 'chatgpt'],
            help="AI model to perform audit"
        )
    else:
        primary_model = st.selectbox(
            "Primary AI Model (Demo Mode)",
            ['claude', 'gemini', 'grok', 'chatgpt']
        )
        st.caption("⚠️  No AI providers configured. Using demo mode.")

with col2:
    audit_stages = st.multiselect(
        "Audit Stages",
        ['neutral', 'adversarial', 'cross_model'],
        default=['neutral', 'adversarial'],
        help="Which audit stages to run"
    )

with col3:
    multi_model = st.checkbox(
        "Multi-AI Mode",
        value=False,
        help="Run audit with multiple AI models for cross-validation"
    )

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# RUN SELECTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("📊 Select Strategy to Audit")

runs = load_all_runs()

if not runs:
    st.info("📭 No backtest runs found. Run a backtest first.")
    st.stop()

# Create run selection
run_options = []
for run in runs[:30]:
    strategy = run.get('strategy_name', 'Unknown')
    run_id = run.get('run_id', 'N/A')[:8]
    timestamp = run.get('timestamp', '')[:16]
    sharpe = run.get('metrics', {}).get('sharpe_ratio', 0)
    run_options.append(f"{run_id} | {strategy} | {timestamp} | Sharpe: {sharpe:.2f}")

selected_option = st.selectbox("Select strategy run to audit", run_options)

if not selected_option:
    st.stop()

# Load run data
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

# ═══════════════════════════════════════════════════════════════════
# RUN AUDIT
# ═══════════════════════════════════════════════════════════════════

st.subheader("🚀 Run Audit")

if st.button("🛡️ Start Audit", type="primary", use_container_width=True):
    with st.spinner("Running multi-stage audit..."):
        try:
            # Create orchestrator
            orchestrator = AuditOrchestrator(default_model=primary_model)
            
            # Run audit
            audit_results = orchestrator.run_full_audit(
                strategy_data=run_data,
                model=primary_model,
                stages=audit_stages
            )
            
            # Store in session
            st.session_state.audit_results = audit_results
            st.success(f"✅ Audit complete! {len(audit_results)} stages executed")
            
        except Exception as e:
            st.error(f"Audit failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════════

if hasattr(st.session_state, 'audit_results'):
    results = st.session_state.audit_results
    
    st.markdown("---")
    st.subheader("📋 Audit Results")
    
    # Tabs for each stage
    stage_tabs = st.tabs([f"{stage.upper()}" for stage in results.keys()])
    
    for idx, (stage_name, audit_result) in enumerate(results.items()):
        with stage_tabs[idx]:
            # Confidence score
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                st.metric("Confidence", f"{audit_result.confidence_score:.1f}/100")
            with col2:
                st.metric("Model", audit_result.model_used)
            with col3:
                st.metric("Risk Flags", len(audit_result.risk_flags))
            
            # Summary
            st.info(f"**Summary:** {audit_result.summary}")
            
            # Findings
            findings = audit_result.findings
            
            # Stage 1: Neutral
            if stage_name == 'neutral':
                if findings.get('strengths'):
                    with st.expander("✅ Strengths", expanded=True):
                        for strength in findings['strengths']:
                            st.success(strength)
                
                if findings.get('weaknesses'):
                    with st.expander("⚠️  Weaknesses", expanded=True):
                        for weakness in findings['weaknesses']:
                            st.warning(weakness)
                
                if findings.get('gaps'):
                    with st.expander("📋 Information Gaps", expanded=False):
                        for gap in findings['gaps']:
                            st.info(gap)
            
            # Stage 2: Adversarial
            elif stage_name == 'adversarial':
                if findings.get('assumption_attacks'):
                    with st.expander("🎯 Assumption Challenges", expanded=True):
                        for attack in findings['assumption_attacks']:
                            st.error(attack)
                
                if findings.get('failure_modes'):
                    with st.expander("💥 Failure Modes", expanded=True):
                        for failure in findings['failure_modes']:
                            st.error(failure)
                
                if findings.get('contradictions'):
                    with st.expander("⚡ Contradictions Detected", expanded=True):
                        for contradiction in findings['contradictions']:
                            st.warning(contradiction)
            
            # Stage 3: Cross-model
            elif stage_name == 'cross_model':
                if findings.get('consensus_items'):
                    with st.expander("✅ Model Consensus", expanded=True):
                        for item in findings['consensus_items']:
                            st.success(item)
                
                if findings.get('disagreements'):
                    with st.expander("⚠️  Model Disagreements", expanded=True):
                        for disagreement in findings['disagreements']:
                            st.warning(f"{disagreement.get('topic', 'Unknown')}: {disagreement.get('conflict', '')}")
    
    # Export
    st.markdown("---")
    st.subheader("📤 Export Audit Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select which stage to export
        export_stage = st.selectbox("Select stage to export", list(results.keys()))
        
        if export_stage and export_stage in results:
            report_md = build_audit_report(
                results[export_stage].__dict__,
                format=AuditReportFormat.MARKDOWN
            )
            
            st.download_button(
                label="📄 Download Markdown Report",
                data=report_md,
                file_name=f"audit_{export_stage}_{results[export_stage].audit_id}.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("📊 Apply to RL/GA Meta-Learning"):
            st.info("Audit findings will be integrated into evolution/RL feedback (Phase X meta-learning)")

# Footer
st.markdown("---")
st.caption("Phase X | AI Audit & Verification Engine")
st.caption("🛡️ HonestAI Protocol: No hallucinations, explicit uncertainty, clear limitations")
st.caption("🔒 Retail-safe: All outputs follow regulatory guidelines")

