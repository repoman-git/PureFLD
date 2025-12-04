"""
AI Cycle Forecaster - LSTM + Hilbert Hybrid

Uses:
- Hilbert transform to extract instantaneous cycle phase & amplitude
- LSTM to learn cycle evolution patterns

Predicts:
- Next trough time
- Next peak time
- Forward composite cycle waveform
- 5-20 day return bias

⚠️  EXPERIMENTAL - AI predictions for educational research only
"""

import numpy as np
import pandas as pd
from scipy.signal import hilbert

try:
    import tensorflow as tf
    from tensorflow.keras import layers, models
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class CycleForecaster:
    """
    AI Cycle Forecaster using:
      - Hilbert transform for cycle decomposition
      - LSTM predictive model for pattern continuation
    
    ⚠️  EXPERIMENTAL - Educational research only
    """

    def __init__(self, lookback=60, forecast_horizon=20):
        """
        Initialize cycle forecaster.
        
        Args:
            lookback: Number of bars to look back
            forecast_horizon: Number of bars to forecast forward
        """
        self.lookback = lookback
        self.horizon = forecast_horizon
        self.model = None
        self.fitted_df = None

    # ------------------------------------------------------------------
    # Hilbert Feature Builder
    # ------------------------------------------------------------------
    def hilbert_features(self, price: pd.Series):
        """
        Extract Hilbert transform features.
        
        Args:
            price: Price series
        
        Returns:
            DataFrame with price, amplitude, phase, delta_phase
        """
        analytic = hilbert(price.values)
        amplitude = np.abs(analytic)
        phase = np.unwrap(np.angle(analytic))
        delta_phase = np.gradient(phase)

        df = pd.DataFrame({
            "price": price.values,
            "amp": amplitude,
            "phase": phase,
            "dphase": delta_phase,
        }, index=price.index)

        return df

    # ------------------------------------------------------------------
    # Prepare supervised learning dataset
    # ------------------------------------------------------------------
    def _create_sequences(self, df):
        """Create LSTM training sequences"""
        X, y = [], []
        values = df.values

        for i in range(self.lookback, len(values) - self.horizon):
            X.append(values[i - self.lookback:i])
            y.append(values[i:i + self.horizon, 0])   # predict price only

        return np.array(X), np.array(y)

    # ------------------------------------------------------------------
    # Build LSTM model
    # ------------------------------------------------------------------
    def build_model(self, n_features):
        """
        Build LSTM neural network.
        
        Args:
            n_features: Number of input features
        
        Returns:
            Keras model
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow not installed. Install with: pip install tensorflow")
        
        model = models.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=(self.lookback, n_features)),
            layers.LSTM(32),
            layers.Dense(self.horizon)
        ])
        model.compile(optimizer="adam", loss="mse")
        self.model = model
        return model

    # ------------------------------------------------------------------
    # Train model
    # ------------------------------------------------------------------
    def fit(self, price: pd.Series, epochs=20, verbose=0):
        """
        Train the forecaster on price data.
        
        Args:
            price: Price series
            epochs: Training epochs
            verbose: Verbosity level
        
        Returns:
            Trained model
        
        ⚠️  EXPERIMENTAL - Results for research only
        """
        df = self.hilbert_features(price)
        X, y = self._create_sequences(df)

        n_features = X.shape[2]
        model = self.build_model(n_features)

        model.fit(X, y, epochs=epochs, verbose=verbose)
        self.fitted_df = df.copy()
        return model

    # ------------------------------------------------------------------
    # Predict next cycle segment
    # ------------------------------------------------------------------
    def predict(self):
        """
        Predict next cycle segment.
        
        Returns:
            Series with forecasted prices
        
        ⚠️  EXPERIMENTAL - Not financial advice
        """
        if self.model is None or self.fitted_df is None:
            raise ValueError("Model not trained. Call fit() first.")
        
        df = self.fitted_df
        last = df.values[-self.lookback:]
        inp = np.expand_dims(last, axis=0)

        pred = self.model.predict(inp, verbose=0)[0]

        index_future = pd.date_range(df.index[-1] + pd.Timedelta(days=1),
                                     periods=self.horizon, freq="D")

        return pd.Series(pred, index=index_future, name="AI_Forecast")

    # ------------------------------------------------------------------
    # Predict next trough & peak (cycle turning points)
    # ------------------------------------------------------------------
    def forecast_turning_points(self, forecast_series: pd.Series):
        """
        Detect local maxima/minima of forecast.
        
        Args:
            forecast_series: Forecasted price series
        
        Returns:
            Dictionary with forecast_troughs and forecast_peaks
        
        ⚠️  EXPERIMENTAL - Educational research only
        """

        series = forecast_series
        troughs = []
        peaks = []

        for i in range(1, len(series) - 1):
            if series.iloc[i] < series.iloc[i - 1] and series.iloc[i] < series.iloc[i + 1]:
                troughs.append(series.index[i])
            if series.iloc[i] > series.iloc[i - 1] and series.iloc[i] > series.iloc[i + 1]:
                peaks.append(series.index[i])

        return {
            "forecast_troughs": troughs,
            "forecast_peaks": peaks
        }


