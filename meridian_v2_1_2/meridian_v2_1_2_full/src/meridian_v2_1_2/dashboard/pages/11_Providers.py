"""
Data & AI Provider Manager

Configure market data sources and AI provider integrations.
Manage API keys, test connections, and set provider priorities.
"""

import streamlit as st
import pandas as pd

from meridian_v2_1_2.providers import (
    load_provider_config,
    save_provider_config,
    get_default_provider_config,
    test_provider_connection,
    test_all_providers
)
from meridian_v2_1_2.ai.ai_config_manager import (
    load_ai_config,
    save_ai_config,
    get_default_ai_config,
    test_ai_provider,
    mask_api_key
)

st.set_page_config(
    page_title="Meridian - Providers",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Data & AI Provider Manager")
st.markdown("*Configure market data sources and AI integrations*")
st.markdown("---")

# Load configurations
provider_config = load_provider_config()
ai_config = load_ai_config()

# Tabs for different sections
tab1, tab2, tab3 = st.tabs(["📊 Market Data", "🤖 AI Providers", "⚙️ Settings"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: MARKET DATA PROVIDERS
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.subheader("📊 Market Data Providers")
    
    st.info("💡 Configure external data sources for real-time and historical market data")
    
    providers = provider_config.get('providers', {})
    
    for provider_name, config in providers.items():
        with st.expander(f"{'✅' if config.get('enabled') else '⚪'} {provider_name.upper()}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{config.get('description', 'No description')}**")
                st.caption(f"Supported: {', '.join(config.get('supported_assets', []))}")
                st.caption(f"Rate Limit: {config.get('rate_limit', 'N/A')} requests/hour")
            
            with col2:
                enabled = st.checkbox(
                    "Enable",
                    value=config.get('enabled', False),
                    key=f"enable_{provider_name}"
                )
                config['enabled'] = enabled
                
                priority = st.number_input(
                    "Priority",
                    min_value=1,
                    max_value=10,
                    value=config.get('priority', 5),
                    key=f"priority_{provider_name}"
                )
                config['priority'] = priority
            
            # API Key input
            if 'api_key' in config:
                current_key = config.get('api_key', '')
                masked_key = mask_api_key(current_key) if current_key else ''
                
                api_key = st.text_input(
                    "API Key",
                    value=masked_key if current_key else '',
                    type="password",
                    key=f"key_{provider_name}",
                    help="Enter your API key (will be masked)"
                )
                
                # Only update if changed
                if api_key and api_key != masked_key:
                    config['api_key'] = api_key
            
            # API Secret (for Alpaca)
            if 'api_secret' in config:
                api_secret = st.text_input(
                    "API Secret",
                    value=mask_api_key(config.get('api_secret', '')) if config.get('api_secret') else '',
                    type="password",
                    key=f"secret_{provider_name}"
                )
                
                if api_secret and api_secret != mask_api_key(config.get('api_secret', '')):
                    config['api_secret'] = api_secret
            
            # Test connection button
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔍 Test Connection", key=f"test_{provider_name}"):
                    with st.spinner("Testing..."):
                        result = test_provider_connection(
                            provider_name,
                            config.get('api_key'),
                            config.get('api_secret')
                        )
                        
                        if result.success:
                            st.success(f"{result.message} ({result.latency_ms:.0f}ms)")
                        else:
                            st.error(result.message)
    
    # Save button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Data Config", type="primary"):
            if save_provider_config(provider_config):
                st.success("✅ Configuration saved!")
                st.rerun()
            else:
                st.error("❌ Save failed")
    
    with col2:
        if st.button("🔄 Reset to Defaults"):
            provider_config = get_default_provider_config()
            save_provider_config(provider_config)
            st.success("Reset to defaults!")
            st.rerun()
    
    with col3:
        if st.button("🧪 Test All Enabled"):
            with st.spinner("Testing all enabled providers..."):
                results = test_all_providers(provider_config)
                
                for provider, result in results.items():
                    if result.success:
                        st.success(f"✅ {provider}: {result.message}")
                    else:
                        st.error(f"❌ {provider}: {result.message}")

# ═══════════════════════════════════════════════════════════════════
# TAB 2: AI PROVIDERS
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.subheader("🤖 AI Provider Configuration")
    
    st.info("💡 Configure LLM integrations for enhanced AI agent capabilities")
    
    ai_providers = ai_config.get('providers', {})
    
    for provider_name, config in ai_providers.items():
        with st.expander(f"{'✅' if config.get('enabled') else '⚪'} {provider_name.upper()}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{config.get('description', 'No description')}**")
                st.caption(f"Model: {config.get('model', 'N/A')}")
                st.caption(f"Context: {config.get('context_window', 'N/A'):,} tokens")
                st.caption(f"Cost: ${config.get('cost_per_1k_tokens', 0):.4f}/1K tokens")
            
            with col2:
                enabled = st.checkbox(
                    "Enable",
                    value=config.get('enabled', False),
                    key=f"ai_enable_{provider_name}"
                )
                config['enabled'] = enabled
            
            # API Key
            current_key = config.get('api_key', '')
            masked_key = mask_api_key(current_key) if current_key else ''
            
            api_key = st.text_input(
                "API Key",
                value=masked_key if current_key else '',
                type="password",
                key=f"ai_key_{provider_name}",
                help="Enter your API key (will be masked)"
            )
            
            if api_key and api_key != masked_key:
                config['api_key'] = api_key
            
            # Model selection
            model = st.text_input(
                "Model Name",
                value=config.get('model', ''),
                key=f"model_{provider_name}",
                help="Model identifier (e.g., gpt-4, claude-3-opus)"
            )
            config['model'] = model
            
            # Test button
            if st.button(f"🧪 Test {provider_name.upper()}", key=f"test_ai_{provider_name}"):
                with st.spinner("Testing AI connection..."):
                    success, message, latency = test_ai_provider(provider_name, config.get('api_key', ''))
                    
                    if success:
                        st.success(f"{message} ({latency:.0f}ms)")
                    else:
                        st.error(message)
    
    # Role assignments
    st.markdown("---")
    st.markdown("### 🎯 AI Role Assignments")
    st.caption("Assign which AI provider to use for each task")
    
    role_assignments = ai_config.get('settings', {}).get('role_assignments', {})
    
    enabled_providers = [p for p, c in ai_providers.items() if c.get('enabled')]
    if not enabled_providers:
        enabled_providers = ['None (configure providers above)']
    
    col1, col2 = st.columns(2)
    
    with col1:
        role_assignments['code_generation'] = st.selectbox(
            "Code Generation",
            enabled_providers,
            index=enabled_providers.index(role_assignments.get('code_generation', enabled_providers[0])) if role_assignments.get('code_generation') in enabled_providers else 0
        )
        
        role_assignments['research_analysis'] = st.selectbox(
            "Research Analysis",
            enabled_providers,
            index=enabled_providers.index(role_assignments.get('research_analysis', enabled_providers[0])) if role_assignments.get('research_analysis') in enabled_providers else 0
        )
        
        role_assignments['report_writing'] = st.selectbox(
            "Report Writing",
            enabled_providers,
            index=enabled_providers.index(role_assignments.get('report_writing', enabled_providers[0])) if role_assignments.get('report_writing') in enabled_providers else 0
        )
    
    with col2:
        role_assignments['risk_commentary'] = st.selectbox(
            "Risk Commentary",
            enabled_providers,
            index=enabled_providers.index(role_assignments.get('risk_commentary', enabled_providers[0])) if role_assignments.get('risk_commentary') in enabled_providers else 0
        )
        
        role_assignments['strategy_generation'] = st.selectbox(
            "Strategy Generation",
            enabled_providers,
            index=enabled_providers.index(role_assignments.get('strategy_generation', enabled_providers[0])) if role_assignments.get('strategy_generation') in enabled_providers else 0
        )
    
    ai_config['settings']['role_assignments'] = role_assignments
    
    # Save AI config
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save AI Config", type="primary"):
            if save_ai_config(ai_config):
                st.success("✅ AI configuration saved!")
                st.rerun()
            else:
                st.error("❌ Save failed")
    
    with col2:
        if st.button("🔄 Reset AI Defaults"):
            ai_config = get_default_ai_config()
            save_ai_config(ai_config)
            st.success("Reset to defaults!")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════
# TAB 3: GENERAL SETTINGS
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.subheader("⚙️ General Settings")
    
    # Market data settings
    st.markdown("### 📊 Market Data Settings")
    
    settings = provider_config.get('settings', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        enabled_data_providers = [p for p, c in providers.items() if c.get('enabled')]
        if enabled_data_providers:
            default_provider = st.selectbox(
                "Default Provider",
                enabled_data_providers,
                index=enabled_data_providers.index(settings.get('default_provider')) if settings.get('default_provider') in enabled_data_providers else 0
            )
            settings['default_provider'] = default_provider
        else:
            st.warning("No providers enabled")
        
        fallback = st.checkbox(
            "Enable Fallback",
            value=settings.get('fallback_enabled', True),
            help="Automatically try next provider if primary fails"
        )
        settings['fallback_enabled'] = fallback
    
    with col2:
        cache_duration = st.number_input(
            "Cache Duration (hours)",
            min_value=1,
            max_value=168,
            value=settings.get('cache_duration_hours', 24)
        )
        settings['cache_duration_hours'] = cache_duration
        
        update_freq = st.selectbox(
            "Update Frequency",
            ['realtime', 'hourly', 'daily', 'weekly'],
            index=['realtime', 'hourly', 'daily', 'weekly'].index(settings.get('update_frequency', 'daily'))
        )
        settings['update_frequency'] = update_freq
    
    provider_config['settings'] = settings
    
    # AI settings
    st.markdown("---")
    st.markdown("### 🤖 AI Settings")
    
    ai_settings = ai_config.get('settings', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        timeout = st.number_input(
            "Timeout (seconds)",
            min_value=10,
            max_value=120,
            value=ai_settings.get('timeout_seconds', 30)
        )
        ai_settings['timeout_seconds'] = timeout
    
    with col2:
        max_retries = st.number_input(
            "Max Retries",
            min_value=1,
            max_value=5,
            value=ai_settings.get('max_retries', 3)
        )
        ai_settings['max_retries'] = max_retries
    
    ai_config['settings'] = ai_settings
    
    # Save all button
    st.markdown("---")
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        data_saved = save_provider_config(provider_config)
        ai_saved = save_ai_config(ai_config)
        
        if data_saved and ai_saved:
            st.success("✅ All configurations saved!")
            st.rerun()
        else:
            st.error("❌ Save failed")
    
    # Status overview
    st.markdown("---")
    st.markdown("### 📊 Configuration Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Data Providers Enabled", sum(1 for c in providers.values() if c.get('enabled')))
        st.metric("Default Provider", settings.get('default_provider', 'None'))
    
    with col2:
        st.metric("AI Providers Enabled", sum(1 for c in ai_providers.items() if c[1].get('enabled')))
        st.metric("Fallback", "On" if settings.get('fallback_enabled') else "Off")

# Footer
st.markdown("---")
st.caption("Phase 7.1 | Provider Configuration Manager")
st.caption("🔒 API keys are stored locally and never transmitted")
st.caption("💡 Real data integration: Phase 8 | LLM integration: Phase 8")

