#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.orchestrator import run_backtest
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Meridian v2.1.2 Control Script')
    parser.add_argument('--config', type=str, help='Path to JSON config file')
    parser.add_argument('--use-tdom', action='store_true', help='Enable TDOM filtering')
    parser.add_argument('--price-data', type=str, required=True, help='Path to price CSV')
    parser.add_argument('--cot-data', type=str, help='Path to COT CSV')
    
    args = parser.parse_args()
    
    # Load config
    if args.config:
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        config = MeridianConfig.from_dict(config_dict)
    else:
        config = MeridianConfig()
    
    # Override TDOM if flag is set
    if args.use_tdom:
        config.seasonality.use_tdom = True
        config.strategy.use_tdom = True
    
    # Load data
    price_df = pd.read_csv(args.price_data, parse_dates=['date'], index_col='date')
    prices = price_df['close'] if 'close' in price_df.columns else price_df.iloc[:, 0]
    
    cot_series = None
    if args.cot_data:
        cot_df = pd.read_csv(args.cot_data, parse_dates=['date'], index_col='date')
        cot_series = cot_df.iloc[:, 0]
    
    # Run backtest
    results = run_backtest(config, prices, cot_series)
    
    # Print results
    print("\n=== MERIDIAN v2.1.2 BACKTEST RESULTS ===")
    print(f"TDOM Enabled: {config.seasonality.use_tdom}")
    print(f"Total Trades: {results['stats']['total_trades']}")
    print(f"Final Equity: ${results['stats']['final_equity']:,.2f}")
    print("\nSignals Preview:")
    print(results['signals'].head(10))

if __name__ == '__main__':
    main()
