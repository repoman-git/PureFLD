"""
AI Provider Configuration Manager

Manage AI/LLM provider settings and API keys.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import shutil
from datetime import datetime


AI_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "data" / "ai_config.json"


def get_default_ai_config() -> Dict[str, Any]:
    """Get default AI provider configuration"""
    return {
        'providers': {
            'chatgpt': {
                'enabled': False,
                'api_key': '',
                'model': 'gpt-4',
                'organization': '',
                'description': 'OpenAI ChatGPT/GPT-4',
                'capabilities': ['code', 'research', 'reports', 'critique', 'generation'],
                'cost_per_1k_tokens': 0.03,
                'context_window': 8192
            },
            'claude': {
                'enabled': False,
                'api_key': '',
                'model': 'claude-3-opus-20240229',
                'description': 'Anthropic Claude 3',
                'capabilities': ['code', 'research', 'reports', 'critique', 'generation'],
                'cost_per_1k_tokens': 0.015,
                'context_window': 200000
            },
            'grok': {
                'enabled': False,
                'api_key': '',
                'model': 'grok-2',
                'description': 'xAI Grok 2',
                'capabilities': ['code', 'research', 'reports'],
                'cost_per_1k_tokens': 0.01,
                'context_window': 32000
            },
            'gemini': {
                'enabled': False,
                'api_key': '',
                'model': 'gemini-pro',
                'description': 'Google Gemini Pro',
                'capabilities': ['code', 'research', 'reports', 'generation'],
                'cost_per_1k_tokens': 0.00125,
                'context_window': 32000
            }
        },
        'settings': {
            'default_provider': 'chatgpt',
            'fallback_enabled': True,
            'timeout_seconds': 30,
            'max_retries': 3,
            'role_assignments': {
                'code_generation': 'chatgpt',
                'research_analysis': 'claude',
                'report_writing': 'claude',
                'risk_commentary': 'grok',
                'strategy_generation': 'chatgpt'
            }
        },
        'last_updated': datetime.now().isoformat()
    }


def load_ai_config() -> Dict[str, Any]:
    """Load AI provider configuration"""
    try:
        if not AI_CONFIG_PATH.exists():
            default_config = get_default_ai_config()
            save_ai_config(default_config)
            return default_config
        
        with open(AI_CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        return config
        
    except Exception as e:
        print(f"Error loading AI config: {e}")
        return get_default_ai_config()


def save_ai_config(config: Dict[str, Any]) -> bool:
    """Save AI provider configuration (atomic write)"""
    try:
        AI_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup
        if AI_CONFIG_PATH.exists():
            backup_path = AI_CONFIG_PATH.with_suffix('.json.backup')
            shutil.copy(AI_CONFIG_PATH, backup_path)
        
        # Atomic write
        temp_path = AI_CONFIG_PATH.with_suffix('.json.tmp')
        
        config['last_updated'] = datetime.now().isoformat()
        
        with open(temp_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        temp_path.replace(AI_CONFIG_PATH)
        
        return True
        
    except Exception as e:
        print(f"Error saving AI config: {e}")
        return False


def update_ai_api_key(provider_name: str, api_key: str) -> bool:
    """Update API key for AI provider"""
    config = load_ai_config()
    
    if provider_name not in config['providers']:
        return False
    
    config['providers'][provider_name]['api_key'] = api_key
    
    return save_ai_config(config)


def get_enabled_ai_providers() -> List[str]:
    """Get list of enabled AI providers"""
    config = load_ai_config()
    
    enabled = []
    for provider_name, provider_config in config['providers'].items():
        if provider_config.get('enabled', False) and provider_config.get('api_key'):
            enabled.append(provider_name)
    
    return enabled


def get_provider_for_role(role: str) -> Optional[str]:
    """Get assigned AI provider for specific role"""
    config = load_ai_config()
    return config.get('settings', {}).get('role_assignments', {}).get(role)


def test_ai_provider(provider_name: str, api_key: str) -> Tuple[bool, str, float]:
    """
    Test AI provider connection.
    
    Args:
        provider_name: Name of AI provider
        api_key: API key to test
    
    Returns:
        (success, message, latency_ms)
    """
    
    start_time = time.time()
    
    # Mock test for now (actual API calls in Phase 8)
    if not api_key or len(api_key) < 10:
        return False, "⚠️  Invalid API key (too short)", 0
    
    # Simulate latency
    time.sleep(0.1)
    latency = (time.time() - start_time) * 1000
    
    # Mock success (actual validation in Phase 8)
    return (
        True,
        f"✅ {provider_name.upper()} configured (validation pending Phase 8)",
        latency
    )


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask API key for display.
    
    Args:
        api_key: Full API key
        visible_chars: Number of chars to show at start
    
    Returns:
        Masked string like "sk-ab***********xyz"
    """
    if not api_key or len(api_key) < visible_chars + 3:
        return "***"
    
    return api_key[:visible_chars] + '*' * 11 + api_key[-3:]

