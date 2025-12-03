"""
Notebook Generation Layer

Bidirectional conversion between strategies and research notebooks.
"""

from .from_strategy import generate_notebook_from_strategy, create_strategy_notebook
from .to_strategy import extract_strategy_template, generate_strategy_module

__all__ = [
    'generate_notebook_from_strategy',
    'create_strategy_notebook',
    'extract_strategy_template',
    'generate_strategy_module'
]

