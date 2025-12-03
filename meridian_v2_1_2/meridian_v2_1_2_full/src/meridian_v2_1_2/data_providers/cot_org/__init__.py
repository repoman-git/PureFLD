"""
CommitmentOfTraders.org Data Provider

Free COT data from commitmentoftraders.org
No API key required!
"""

from .cot_org_fetcher import COTOrgFetcher, fetch_cot_data

__all__ = ['COTOrgFetcher', 'fetch_cot_data']

