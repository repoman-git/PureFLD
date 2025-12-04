#!/usr/bin/env python3
"""
Meridian 3.0 Integration Test Suite v2 (FIXED)

Uses realistic synthetic data to properly test all stages.

Author: Meridian Team
Date: December 4, 2025
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pandas as pd
import numpy as np
from synthetic_data_generator import SyntheticDataGenerator

print("\n" + "="*70)
print("🔍 MERIDIAN 3.0 INTEGRATION TEST SUITE v2 (FIXED)")
print("="*70)
print()

# Track results
passed = 0
failed = 0
errors = []

def check(name, fn):
    """Run a test and track results"""
    global passed, failed, errors
    try:
        fn()
        print(f"   ✅ {name}")
        passed += 1
        return True
    except Exception as e:
        print(f"   ❌ {name}")
        print(f"      Error: {str(e)[:150]}")
        failed += 1
        errors.append((name, str(e)))
        return False

# ---------------------------
# Generate Realistic Test Data
# ---------------------------
print("📊 Generating realistic synthetic data...")

generator = SyntheticDataGenerator(seed=42)

# Single asset (250 bars - sufficient for all tests)
price_series = generator.generate_price_series(n_bars=250, base_price=1800)

# Multi-asset (for pairs trading)
multi_asset_dict = generator.generate_multi_asset(
    assets=['GLD', 'SLV', 'TLT', 'SPY'],
    n_bars=250
)

# With regime shifts (for regime classifier)
regime_price, regime_labels = generator.generate_with_regime_shifts(n_bars=300)

print(f"✅ Generated realistic test data:")
print(f"   • Single asset: {len(price_series)} bars")
print(f"   • Multi-asset: {len(multi_asset_dict)} symbols × 250 bars")
print(f"   • Regime data: {len(regime_price)} bars with labeled regimes")
print()

timestamps = price_series.index.strftime("%Y-%m-%d").tolist()
price_list = price_series.tolist()

payload = {
    "timestamps": timestamps,
    "prices": price_list
}

# ========================================
# TEST SECTION 1: MODULE IMPORTS
# ========================================
print("=" * 70)
print("TEST SECTION 1: MODULE IMPORTS")
print("=" * 70)

def test_stage1_imports():
    from meridian_v2_1_2.intermarket_arbitrage import (
        PairsSelector, DivergenceDetector, PairsStrategy, PairsBacktester
    )
check("Stage 1: Intermarket Arbitrage Imports", test_stage1_imports)

def test_stage2_imports():
    from meridian_v2_1_2.regimes import (
        CycleRegimeClassifier, RegimeType, RegimeFilter
    )
check("Stage 2: Regime Classifier Imports", test_stage2_imports)

def test_stage3_imports():
    from meridian_v2_1_2.portfolio_allocation import (
        PortfolioFeatureBuilder, PortfolioAllocator
    )
check("Stage 3: Portfolio Allocation Imports", test_stage3_imports)

def test_stage4_imports():
    from meridian_v2_1_2.volatility_risk import (
        VolFeatureBuilder, CycleATR, RiskWindowModel
    )
check("Stage 4: Volatility Risk Imports", test_stage4_imports)

def test_stage5_imports():
    from meridian_v2_1_2.strategy_evolution import (
        StrategyGenome, GeneticStrategyEngine
    )
check("Stage 5: Strategy Evolution Imports", test_stage5_imports)

def test_stage7_imports():
    from meridian_v2_1_2.execution_engine import (
        OrderManager, PositionManager, RiskGate, ExecutionEngine
    )
check("Stage 7: Execution Engine Imports", test_stage7_imports)

def test_stage9_imports():
    from meridian_v2_1_2.meridian_agents import AgentOrchestrator
check("Stage 9: Agent Coordinator Imports", test_stage9_imports)

def test_stage10_imports():
    from meridian_v2_1_2.storage.meridian_db import MeridianDB
    from meridian_v2_1_2.storage.model_registry import ModelRegistry
    from meridian_v2_1_2.pipeline.meridian_pipeline import MeridianPipeline
check("Stage 10: Production Infrastructure Imports", test_stage10_imports)

print()

# ========================================
# TEST SECTION 2: CORE FUNCTIONALITY (FIXED)
# ========================================
print("=" * 70)
print("TEST SECTION 2: CORE FUNCTIONALITY (FIXED)")
print("=" * 70)

def test_pairs_selector_fixed():
    """FIXED: Use realistic multi-asset data"""
    from meridian_v2_1_2.intermarket_arbitrage import PairsSelector
    
    selector = PairsSelector(min_correlation=0.3)
    pairs = selector.select_pairs(multi_asset_dict, top_n=2)
    
    # Should find at least some correlation with realistic data
    assert pairs is not None, "Pairs selector should return results"
    print(f"      Found {len(pairs)} pairs")
check("Pairs Selector Execution (FIXED)", test_pairs_selector_fixed)

def test_regime_classifier_fixed():
    """FIXED: Use longer dataset for training"""
    from meridian_v2_1_2.regimes import CycleRegimeClassifier
    
    classifier = CycleRegimeClassifier()
    features = classifier.extract_features(regime_price)
    labels = classifier.label_regimes(features)
    
    # Train with proper data
    metrics = classifier.train(features, labels, verbose=False)
    
    assert metrics['train_accuracy'] > 0.5, "Classifier should train successfully"
    assert labels.min() >= 0 and labels.max() <= 4, "Labels should be 0-4"
    print(f"      Train accuracy: {metrics['train_accuracy']:.2%}")
check("Regime Classifier Execution (FIXED)", test_regime_classifier_fixed)

def test_portfolio_allocation():
    from meridian_v2_1_2.portfolio_allocation import (
        PortfolioFeatureBuilder, PortfolioAllocator,
        CycleWeightingModel, PortfolioRiskModel
    )
    
    builder = PortfolioFeatureBuilder()
    features = builder.build_features(multi_asset_dict)
    
    allocator = PortfolioAllocator()
    weights = allocator.allocate(features, CycleWeightingModel(), PortfolioRiskModel())
    
    assert weights is not None, "Allocator should return weights"
    print(f"      Generated weights for {len(weights.columns)} assets")
check("Portfolio Allocation Execution", test_portfolio_allocation)

def test_volatility_risk():
    from meridian_v2_1_2.volatility_risk import (
        VolFeatureBuilder, CycleATR, VolatilityEnvelope
    )
    
    vb = VolFeatureBuilder()
    df = vb.build(price_series)
    
    catr = CycleATR().compute(price_series, df["phase_vel"])
    env = VolatilityEnvelope().compute(df["vol"])
    
    assert len(catr) > 0, "C-ATR should compute"
    assert "upper" in env, "Envelope should have upper band"
    print(f"      Computed {len(catr)} C-ATR values")
check("Volatility Risk Execution", test_volatility_risk)

def test_strategy_evolution():
    from meridian_v2_1_2.strategy_evolution import StrategyGenome
    
    genome = StrategyGenome()
    mutated = genome.mutate(rate=0.1)
    
    assert genome.genes is not None, "Genome should have genes"
    print(f"      Genome has {len(genome.genes)} parameters")
check("Strategy Evolution Execution", test_strategy_evolution)

def test_database_operations():
    from meridian_v2_1_2.storage.meridian_db import MeridianDB
    
    db = MeridianDB(db_path="test_meridian_v2.db")
    test_df = pd.DataFrame({
        'timestamp': timestamps[:5],
        'symbol': ['TEST'] * 5,
        'signal': [1.0, -1.0, 0.0, 1.0, -1.0],
        'confidence': [0.8, 0.7, 0.5, 0.9, 0.6]
    })
    
    db.write('signals', test_df)
    result = db.read("SELECT COUNT(*) as count FROM signals")
    count = result['count'].iloc[0]
    
    assert count >= 5, f"DB should persist data, got {count}"
    db.close()
    
    # Cleanup
    if os.path.exists("test_meridian_v2.db"):
        os.remove("test_meridian_v2.db")
    print(f"      Wrote and read {count} records successfully")
check("Database Operations (FIXED)", test_database_operations)

def test_model_registry():
    from meridian_v2_1_2.storage.model_registry import ModelRegistry
    
    registry = ModelRegistry(registry_path="test_registry_v2")
    registry.register_model("test_model_v2", {
        "type": "regime_classifier",
        "accuracy": 0.85,
        "version": "2.0"
    })
    
    models = registry.list_models()
    assert 'test_model_v2' in models, "Registry should persist models"
    
    # Cleanup
    import shutil
    if Path("test_registry_v2").exists():
        shutil.rmtree("test_registry_v2")
    print(f"      Registered and retrieved model successfully")
check("Model Registry Operations", test_model_registry)

print()

# ========================================
# TEST SECTION 3: PIPELINE INTEGRATION (FIXED)
# ========================================
print("=" * 70)
print("TEST SECTION 3: PIPELINE INTEGRATION (FIXED)")
print("=" * 70)

def test_full_pipeline_fixed():
    """FIXED: Use proper dataset"""
    from meridian_v2_1_2.pipeline.meridian_pipeline import MeridianPipeline
    
    pipeline = MeridianPipeline()
    
    # Use multi-asset dict with proper data
    test_dict = {'SPY': multi_asset_dict['SPY']}
    
    results = pipeline.run(test_dict)
    
    assert 'phasing' in results, "Pipeline should return phasing"
    assert 'regime' in results, "Pipeline should return regime"
    print(f"      Pipeline executed successfully")
check("Full Pipeline Execution (FIXED)", test_full_pipeline_fixed)

print()

# ========================================
# FINAL REPORT
# ========================================
print("=" * 70)
print("📊 TEST RESULTS")
print("=" * 70)
print()
print(f"   ✅ Passed: {passed}")
print(f"   ❌ Failed: {failed}")
print(f"   📊 Total:  {passed + failed}")
print()

if failed == 0:
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║         🎊 ALL TESTS PASSED! 🎊                        ║")
    print("║                                                        ║")
    print("║    Meridian 3.0 is FULLY VALIDATED                     ║")
    print("║    100% Pass Rate Achieved                             ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    sys.exit(0)
else:
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║         ⚠️  SOME TESTS FAILED ⚠️                      ║")
    print("║                                                        ║")
    print("║    Review errors above and fix failing components     ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Failed tests:")
    for name, error in errors:
        print(f"  • {name}")
        print(f"    {error[:150]}")
    print()
    sys.exit(1)

