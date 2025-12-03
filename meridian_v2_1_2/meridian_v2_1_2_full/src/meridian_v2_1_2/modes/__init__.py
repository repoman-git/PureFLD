"""
Mode Separation for Meridian v2.1.2

Separates research, paper trading, and live trading modes for safety and clarity.
"""

from .research_config import ResearchSettings, validate_research_mode
from .paper_config import PaperSettings, validate_paper_mode
from .live_config import LiveSettings, validate_live_mode
from .mode_router import route_by_mode

__all__ = [
    'ResearchSettings',
    'PaperSettings',
    'LiveSettings',
    'validate_research_mode',
    'validate_paper_mode',
    'validate_live_mode',
    'route_by_mode',
]

