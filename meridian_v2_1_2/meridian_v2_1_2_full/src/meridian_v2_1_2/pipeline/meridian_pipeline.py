"""
Meridian 3.0 Pipeline - Complete end-to-end orchestrator

Author: Meridian Team
Date: December 4, 2025
"""

import pandas as pd
from typing import Dict
from meridian_v2_1_2.hurst.hurst_phasing import HurstPhasingEngine
from meridian_v2_1_2.regimes import CycleRegimeClassifier
from meridian_v2_1_2.portfolio_allocation import PortfolioAllocator, CycleWeightingModel, PortfolioRiskModel
from meridian_v2_1_2.storage.meridian_db import db

class MeridianPipeline:
    """Complete end-to-end Meridian pipeline"""
    
    def __init__(self):
        self.phaser = HurstPhasingEngine(nominal_periods=[20, 40, 80])
        self.regime_classifier = CycleRegimeClassifier()
        self.allocator = PortfolioAllocator()
        self.cycle_model = CycleWeightingModel()
        self.risk_model = PortfolioRiskModel()
    
    def run(self, price_dict: Dict[str, pd.Series]) -> Dict:
        """Run complete pipeline"""
        results = {}
        
        # Phase 1: Cycle Analysis
        print("Phase 1: Cycle Analysis...")
        results['phasing'] = {}
        for symbol, prices in price_dict.items():
            try:
                results['phasing'][symbol] = self.phaser.compute_phase(prices, 40)
            except Exception as e:
                print(f"  ⚠️ {symbol} phasing failed: {e}")
        
        # Phase 2: Regime Classification
        print("Phase 2: Regime Classification...")
        # Use first symbol as market proxy
        first_symbol = list(price_dict.keys())[0]
        features = self.regime_classifier.extract_features(price_dict[first_symbol])
        labels = self.regime_classifier.label_regimes(features)
        
        if not self.regime_classifier.is_trained:
            self.regime_classifier.train(features, labels, verbose=False)
        
        results['regime'] = self.regime_classifier.predict(features)
        
        # Phase 3: Storage
        print("Phase 3: Storing results...")
        try:
            db.write('regimes', pd.DataFrame({
                'timestamp': results['regime'].index.astype(str),
                'regime': results['regime']['regime'],
                'confidence': results['regime']['regime_confidence']
            }))
        except Exception as e:
            print(f"  ⚠️ Storage failed: {e}")
        
        print("✅ Pipeline complete!")
        return results

pipeline = MeridianPipeline()

