"""
Connection Tester for External APIs

Validates API connections at startup.
"""

from typing import Dict, Any, Optional

from .external_config import ExternalConfig
from .openbb_adapter import OpenBBAdapter
from .alpaca_adapter import AlpacaAdapter


class ConnectionTester:
    """
    Tests external API connections.
    
    Validates:
    - API keys present
    - Connections work
    - Account status
    - Trading permissions
    """
    
    def __init__(self, config: Optional[ExternalConfig] = None):
        """
        Initialize connection tester.
        
        Args:
            config: External configuration
        """
        self.config = config or ExternalConfig()
        self.results = {}
    
    def test_all(self) -> Dict[str, Any]:
        """
        Test all configured connections.
        
        Returns:
            Dict with test results
        """
        results = {
            'overall_status': 'ok',
            'openbb': None,
            'alpaca': None,
            'errors': []
        }
        
        # Test OpenBB
        if self.config.use_openbb:
            try:
                openbb = OpenBBAdapter(self.config)
                results['openbb'] = openbb.test_connection()
                
                if not results['openbb']['connection_ok']:
                    results['overall_status'] = 'partial'
                    if results['openbb'].get('error'):
                        results['errors'].append(f"OpenBB: {results['openbb']['error']}")
            except Exception as e:
                results['openbb'] = {'error': str(e), 'connection_ok': False}
                results['overall_status'] = 'partial'
                results['errors'].append(f"OpenBB: {e}")
        
        # Test Alpaca
        if self.config.use_alpaca:
            try:
                alpaca = AlpacaAdapter(self.config)
                results['alpaca'] = alpaca.test_connection()
                
                if not results['alpaca']['connection_ok']:
                    results['overall_status'] = 'partial'
                    if results['alpaca'].get('error'):
                        results['errors'].append(f"Alpaca: {results['alpaca']['error']}")
            except Exception as e:
                results['alpaca'] = {'error': str(e), 'connection_ok': False}
                results['overall_status'] = 'partial'
                results['errors'].append(f"Alpaca: {e}")
        
        # Set overall status
        if results['errors']:
            if results['openbb'] is None and results['alpaca'] is None:
                results['overall_status'] = 'failed'
            else:
                results['overall_status'] = 'partial'
        
        self.results = results
        return results
    
    def print_results(self):
        """Print connection test results"""
        if not self.results:
            self.test_all()
        
        print("\n" + "="*60)
        print("EXTERNAL API CONNECTION TEST")
        print("="*60)
        
        print(f"\nOverall Status: {self.results['overall_status'].upper()}")
        
        if self.results.get('openbb'):
            print("\n--- OpenBB ---")
            openbb = self.results['openbb']
            print(f"  Enabled: {openbb.get('enabled', False)}")
            print(f"  Has Key: {openbb.get('has_key', False)}")
            print(f"  Connection: {'✓' if openbb.get('connection_ok') else '✗'}")
            if openbb.get('error'):
                print(f"  Error: {openbb['error']}")
        
        if self.results.get('alpaca'):
            print("\n--- Alpaca ---")
            alpaca = self.results['alpaca']
            print(f"  Enabled: {alpaca.get('enabled', False)}")
            print(f"  Has Keys: {alpaca.get('has_keys', False)}")
            print(f"  Connection: {'✓' if alpaca.get('connection_ok') else '✗'}")
            print(f"  Live Trading: {alpaca.get('live_trading', False)}")
            print(f"  Paper Trading: {alpaca.get('paper_trading', True)}")
            if alpaca.get('error'):
                print(f"  Error: {alpaca['error']}")
        
        if self.results['errors']:
            print("\nErrors:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*60 + "\n")


def test_connections(config: Optional[ExternalConfig] = None) -> Dict[str, Any]:
    """
    Convenience function to test connections.
    
    Args:
        config: External configuration
    
    Returns:
        Test results dict
    """
    tester = ConnectionTester(config)
    return tester.test_all()


