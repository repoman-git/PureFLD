"""
Parameter Space Definitions

Define searchable parameter ranges for different strategy types.
Format: {param_name: (min, max) for numeric, [options] for categorical}
"""

# FLD Strategy Parameter Space
FLD_PARAM_SPACE = {
    'cycle_length': (5, 80),           # Cycle lookback period
    'displacement': (1, 40),           # FLD displacement/offset
    'allow_short': [True, False],      # Enable short positions
    'contracts': (1, 5),               # Position size
    'stop_loss': (0.02, 0.10),        # Stop loss %
    'take_profit': (0.05, 0.30),      # Take profit %
    'cot_threshold': (0.0, 0.3),      # COT filter threshold
}

# COT Strategy Parameter Space
COT_PARAM_SPACE = {
    'cot_lookback': (10, 100),        # COT data lookback
    'cot_threshold': (0.1, 0.5),      # Threshold for signal
    'position_size': (1, 5),          # Contract size
    'stop_loss': (0.02, 0.10),
    'take_profit': (0.05, 0.30),
    'use_trend_filter': [True, False],
}

# Generic Strategy Parameter Space (for experimentation)
GENERIC_PARAM_SPACE = {
    'lookback': (5, 200),
    'threshold': (0.0, 1.0),
    'position_size': (1, 10),
    'stop_loss': (0.01, 0.15),
    'take_profit': (0.03, 0.40),
}


def get_param_space(strategy_name: str) -> dict:
    """
    Get parameter space for a given strategy.
    
    Args:
        strategy_name: Name of strategy ('FLD', 'COT', etc.)
    
    Returns:
        Parameter space dictionary
    """
    spaces = {
        'FLD': FLD_PARAM_SPACE,
        'COT': COT_PARAM_SPACE,
        'GENERIC': GENERIC_PARAM_SPACE,
    }
    
    return spaces.get(strategy_name.upper(), GENERIC_PARAM_SPACE)


def validate_params(params: dict, param_space: dict) -> bool:
    """
    Validate that parameters are within defined space.
    
    Args:
        params: Parameter dictionary to validate
        param_space: Parameter space definition
    
    Returns:
        True if valid, False otherwise
    """
    for key, value in params.items():
        if key not in param_space:
            continue  # Allow extra params not in space
        
        space_def = param_space[key]
        
        # Check numeric ranges
        if isinstance(space_def, tuple):
            if not (space_def[0] <= value <= space_def[1]):
                return False
        
        # Check categorical options
        elif isinstance(space_def, list):
            if value not in space_def:
                return False
    
    return True


