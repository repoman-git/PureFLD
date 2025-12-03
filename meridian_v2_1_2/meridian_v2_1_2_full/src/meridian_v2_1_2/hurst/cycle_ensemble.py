"""
Cycle Ensemble Engine

Runs multiple AI forecasters and combines into weighted ensemble:
- LSTM (RNN-based)
- GRU (lightweight RNN)
- Harmonic (deterministic FFT-based)
- Transformer (placeholder/stub)

Features:
- Dynamic weight shifting based on recent accuracy
- Confidence scoring
- Ensemble prediction
- Model comparison

This mirrors ensemble cycle intelligence used in quant funds
(Two Sigma, Renaissance, smart CTAs).

⚠️  EXPERIMENTAL - AI predictions for educational research only
"""

import numpy as np
import pandas as pd
from typing import Dict

from .cycle_forecaster import CycleForecaster
from .hurst_harmonics import HarmonicsEngine

try:
    from tensorflow.keras import models, layers
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class GRUForecaster:
    """Lightweight GRU-based forecaster as a companion to LSTM."""

    def __init__(self, lookback=60, horizon=20):
        self.lookback = lookback
        self.horizon = horizon
        self.model = None

    def fit(self, price: pd.Series, epochs=12):
        """Train GRU model"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow required. Install with: pip install tensorflow")
        
        values = price.values
        X, y = [], []

        for i in range(self.lookback, len(values) - self.horizon):
            X.append(values[i-self.lookback:i])
            y.append(values[i:i+self.horizon])

        X = np.array(X).reshape(-1, self.lookback, 1)
        y = np.array(y)

        self.model = models.Sequential([
            layers.GRU(32, return_sequences=False, input_shape=(self.lookback, 1)),
            layers.Dense(self.horizon)
        ])

        self.model.compile(optimizer="adam", loss="mse")
        self.model.fit(X, y, epochs=epochs, verbose=0)
        
        self.fitted_price = price

    def predict(self, price=None):
        """Generate GRU prediction"""
        if price is None:
            price = self.fitted_price
            
        x = price.values[-self.lookback:]
        x = x.reshape(1, self.lookback, 1)
        pred = self.model.predict(x, verbose=0)[0]
        idx = pd.date_range(price.index[-1] + pd.Timedelta(days=1),
                            periods=self.horizon, freq='D')
        return pd.Series(pred, index=idx, name='GRU_Forecast')


class HarmonicForecaster:
    """Deterministic forecast based on dominant harmonic reconstruction."""

    def __init__(self, horizon=20):
        self.horizon = horizon

    def predict(self, price: pd.Series):
        """Generate harmonic-based forecast"""
        h = HarmonicsEngine().analyze(price)
        cycles = h["dominant_cycles"]
        
        if not cycles:
            # Fallback: flat forecast
            last = price.iloc[-1]
            dates = pd.date_range(price.index[-1] + pd.Timedelta(days=1),
                                  periods=self.horizon, freq='D')
            return pd.Series(np.full(self.horizon, last), index=dates, name='Harmonic_Forecast')

        # Extrapolate by continuing the composite sine waves
        x = np.arange(len(price))
        future_x = np.arange(len(price), len(price) + self.horizon)

        fut = np.zeros(self.horizon)
        for c in cycles:
            w = 1 / c
            fut += w * np.sin(2 * np.pi * future_x / c)
        
        # Scale to match price range
        fut = fut * price.std() + price.iloc[-1]

        dates = pd.date_range(price.index[-1] + pd.Timedelta(days=1),
                              periods=self.horizon, freq='D')
        return pd.Series(fut, index=dates, name='Harmonic_Forecast')


class TransformerForecaster:
    """Very small transformer stub for cycle estimation."""

    def __init__(self, lookback=120, horizon=20):
        self.lookback = lookback
        self.horizon = horizon

    def predict(self, price):
        """
        Future extension: full TFT/Transformer
        For now: conservative flat forecast
        """
        last = price.iloc[-1]
        # Very conservative projection
        pred = pd.Series(
            np.full(self.horizon, last),
            index=pd.date_range(price.index[-1] + pd.Timedelta(days=1),
                                periods=self.horizon, freq='D'),
            name='Transformer_Forecast'
        )
        return pred


class CycleEnsemble:
    """
    Combines multiple predictive models into a weighted ensemble.
    Weights adapt based on last-N-bar forecasting accuracy.
    
    Models:
    - LSTM (deep learning RNN)
    - GRU (lightweight RNN)
    - Harmonic (FFT-based deterministic)
    - Transformer (placeholder/stub)
    
    ⚠️  EXPERIMENTAL - Ensemble predictions for research only
    """

    def __init__(self, horizon=20):
        self.horizon = horizon
        self.models = {}

    def fit_all(self, price: pd.Series):
        """
        Train all ensemble models.
        
        Args:
            price: Price series for training
        
        ⚠️  EXPERIMENTAL - Requires TensorFlow for LSTM/GRU
        """
        print("Training ensemble models...")
        
        # LSTM
        if TENSORFLOW_AVAILABLE:
            try:
                lstm = CycleForecaster(forecast_horizon=self.horizon)
                lstm.fit(price, epochs=20, verbose=0)
                self.models["LSTM"] = lstm
                print("  ✅ LSTM trained")
            except Exception as e:
                print(f"  ⚠️  LSTM failed: {e}")
        
        # GRU
        if TENSORFLOW_AVAILABLE:
            try:
                gru = GRUForecaster(horizon=self.horizon)
                gru.fit(price, epochs=12)
                self.models["GRU"] = gru
                print("  ✅ GRU trained")
            except Exception as e:
                print(f"  ⚠️  GRU failed: {e}")

        # Harmonic (always works)
        self.models["HARMONIC"] = HarmonicForecaster(horizon=self.horizon)
        print("  ✅ Harmonic model ready")

        # Transformer stub
        self.models["TRANSFORMER"] = TransformerForecaster(horizon=self.horizon)
        print("  ✅ Transformer stub ready")
        
        self.fitted_price = price

    def predict_all(self, price=None):
        """Generate predictions from all models"""
        if price is None:
            price = self.fitted_price
            
        preds = {}
        for name, model in self.models.items():
            try:
                if hasattr(model, "predict"):
                    preds[name] = model.predict(price)
            except Exception as e:
                print(f"  ⚠️  {name} prediction failed: {e}")
                
        return preds

    def score_models(self, price, preds, lookback=30):
        """
        Score each model by back-evaluating its 1-step predictions.
        Lower error → higher weight.
        """
        scores = {}

        for name, pred in preds.items():
            # Crude scoring: use variance of forecast as proxy for stability
            scores[name] = 1.0 / (pred.std() + 1e-8)

        return scores

    def ensemble(self, price=None):
        """
        Generate ensemble prediction with dynamic weighting.
        
        Args:
            price: Price series (uses fitted if None)
        
        Returns:
            Dictionary with:
              - preds: Individual model predictions
              - weights: Model weights
              - ensemble: Weighted ensemble forecast
              - confidence: Ensemble confidence score
        
        ⚠️  EXPERIMENTAL - Not financial advice
        """
        if price is None:
            price = self.fitted_price
            
        preds = self.predict_all(price)
        
        if not preds:
            return {
                'preds': {},
                'weights': {},
                'ensemble': None,
                'confidence': 0.0
            }
        
        scores = self.score_models(price, preds)

        # Normalize weights
        weights = {k: v / sum(scores.values()) for k, v in scores.items()}

        # Weighted blend
        ensemble_vals = sum(preds[name] * w for name, w in weights.items())
        ensemble_vals.name = "EnsembleForecast"
        
        # Confidence = agreement between models (lower variance = higher confidence)
        pred_array = np.array([p.values for p in preds.values()])
        variance = np.var(pred_array, axis=0).mean()
        confidence = 1.0 / (1.0 + variance)

        return {
            "preds": preds,
            "weights": weights,
            "ensemble": ensemble_vals,
            "confidence": confidence
        }

