"""
Portfolio Feature Builder (Stage 3)

Extracts cycle, risk, and intermarket features for portfolio allocation.

This module combines insights from:
- Cycle analysis (amplitude, phase, harmonics)
- Regime classification (market context)
- Intermarket relationships (correlations, pressure)
- Risk metrics (volatility, drawdown)

Author: Meridian Team
Date: December 4, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PortfolioFeatures:
    """Container for portfolio features per asset"""
    symbol: str
    price: pd.Series
    cycle_amplitude: pd.Series
    cycle_slope: pd.Series
    phase_velocity: pd.Series
    volatility: pd.Series
    regime: pd.Series
    regime_confidence: pd.Series
    intermarket_pressure: pd.Series
    turning_point_proximity: pd.Series
    risk_score: pd.Series
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame"""
        return pd.DataFrame({
            'price': self.price,
            'cycle_amplitude': self.cycle_amplitude,
            'cycle_slope': self.cycle_slope,
            'phase_velocity': self.phase_velocity,
            'volatility': self.volatility,
            'regime': self.regime,
            'regime_confidence': self.regime_confidence,
            'intermarket_pressure': self.intermarket_pressure,
            'turning_point_proximity': self.turning_point_proximity,
            'risk_score': self.risk_score
        })


class PortfolioFeatureBuilder:
    """
    Extract cycle + risk + intermarket features for portfolio allocation.
    
    This class builds comprehensive features for each asset in the portfolio,
    combining cycle dynamics, regime context, and intermarket relationships.
    
    Example:
        >>> builder = PortfolioFeatureBuilder(cycle_periods=[20, 40, 80])
        >>> 
        >>> features = builder.build_features(
        ...     price_dict={'SPY': spy_prices, 'TLT': tlt_prices},
        ...     regime_dict={'SPY': spy_regime, 'TLT': tlt_regime}
        ... )
        >>> 
        >>> # Features ready for allocation
        >>> for symbol, feature_df in features.items():
        ...     print(f"{symbol}: {len(feature_df.columns)} features")
    """
    
    def __init__(self, cycle_periods: List[int] = [20, 40, 80]):
        """
        Initialize feature builder.
        
        Args:
            cycle_periods: Cycle periods to analyze
        """
        self.cycle_periods = cycle_periods
    
    def build_features(
        self,
        price_dict: Dict[str, pd.Series],
        regime_dict: Optional[Dict[str, pd.DataFrame]] = None,
        phasing_dict: Optional[Dict[str, Dict]] = None,
        harmonics_dict: Optional[Dict[str, Dict]] = None,
        forecast_dict: Optional[Dict[str, pd.Series]] = None,
        intermarket_pressure: Optional[Dict[str, float]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Build features for all assets in portfolio.
        
        Args:
            price_dict: Dictionary of {symbol: price_series}
            regime_dict: Dictionary of {symbol: regime_predictions} (optional)
            phasing_dict: Dictionary of {symbol: phasing_results} (optional)
            harmonics_dict: Dictionary of {symbol: harmonics_results} (optional)
            forecast_dict: Dictionary of {symbol: forecast_series} (optional)
            intermarket_pressure: Dictionary of {symbol: pressure_value} (optional)
            
        Returns:
            Dictionary of {symbol: feature_dataframe}
        """
        features = {}
        
        for symbol in price_dict.keys():
            price = price_dict[symbol]
            
            # Build features for this asset
            feature_df = self._build_asset_features(
                symbol=symbol,
                price=price,
                regime=regime_dict.get(symbol) if regime_dict else None,
                phasing=phasing_dict.get(symbol) if phasing_dict else None,
                harmonics=harmonics_dict.get(symbol) if harmonics_dict else None,
                forecast=forecast_dict.get(symbol) if forecast_dict else None,
                pressure=intermarket_pressure.get(symbol, 0.0) if intermarket_pressure else 0.0
            )
            
            features[symbol] = feature_df
        
        return features
    
    def _build_asset_features(
        self,
        symbol: str,
        price: pd.Series,
        regime: Optional[pd.DataFrame],
        phasing: Optional[Dict],
        harmonics: Optional[Dict],
        forecast: Optional[pd.Series],
        pressure: float
    ) -> pd.DataFrame:
        """Build features for a single asset"""
        df = pd.DataFrame(index=price.index)
        df['price'] = price
        
        # === Price Features ===
        df['returns'] = price.pct_change()
        df['returns_5'] = price.pct_change(5)
        df['returns_20'] = price.pct_change(20)
        
        # === Volatility Features ===
        df['volatility'] = price.pct_change().rolling(20).std()
        df['volatility_60'] = price.pct_change().rolling(60).std()
        df['vol_ratio'] = df['volatility'] / (df['volatility_60'] + 1e-10)
        
        # ATR
        high_low_range = price.rolling(14).max() - price.rolling(14).min()
        df['atr'] = high_low_range.rolling(14).mean()
        df['atr_pct'] = df['atr'] / price
        
        # === Cycle Features ===
        if harmonics:
            # Cycle amplitude across periods
            amp_cols = []
            for period in self.cycle_periods:
                if period in harmonics:
                    harm = harmonics[period]
                    amp = harm.get('amplitude', harm.get('cycle_amplitude', 0))
                    
                    if isinstance(amp, (int, float)):
                        df[f'amp_{period}'] = amp
                    elif hasattr(amp, '__iter__'):
                        df[f'amp_{period}'] = pd.Series(amp, index=price.index)
                    
                    amp_cols.append(f'amp_{period}')
            
            # Total and average amplitude
            if amp_cols:
                df['amp_total'] = df[amp_cols].sum(axis=1)
                df['amp_mean'] = df[amp_cols].mean(axis=1)
                df['amp_trend'] = df['amp_total'].diff(5)
        else:
            # Fallback: use volatility as proxy
            df['amp_total'] = df['volatility'] * 10
            df['amp_mean'] = df['amp_total']
            df['amp_trend'] = df['amp_total'].diff(5)
        
        # === Phase Features ===
        if phasing:
            phase_vel_cols = []
            for period in self.cycle_periods:
                if period in phasing:
                    phase_dict = phasing[period]
                    
                    if 'phase' in phase_dict:
                        phase = phase_dict['phase']
                        if isinstance(phase, pd.Series):
                            df[f'phase_{period}'] = phase
                            df[f'phase_vel_{period}'] = phase.diff()
                            phase_vel_cols.append(f'phase_vel_{period}')
            
            # Average phase velocity
            if phase_vel_cols:
                df['phase_velocity'] = df[phase_vel_cols].mean(axis=1)
            else:
                df['phase_velocity'] = 0
            
            # Turning point proximity
            df['tp_proximity'] = 0
            if self.cycle_periods and len(self.cycle_periods) > 1:
                main_period = self.cycle_periods[1]  # Use middle period
                if main_period in phasing and 'troughs' in phasing[main_period]:
                    troughs = phasing[main_period]['troughs']
                    for trough in troughs:
                        if trough in df.index:
                            df.loc[trough, 'tp_proximity'] = 1
        else:
            df['phase_velocity'] = 0
            df['tp_proximity'] = 0
        
        # === Forecast Features ===
        if forecast is not None and len(forecast) > 1:
            # Forecast slope
            forecast_slope = (forecast.iloc[-1] - forecast.iloc[0]) / len(forecast)
            df['forecast_slope'] = forecast_slope
            
            # Forecast divergence from price
            if len(forecast) > 0 and len(price) > 0:
                current_price = price.iloc[-1]
                forecast_value = forecast.iloc[-1]
                df['forecast_divergence'] = (forecast_value - current_price) / (current_price + 1e-10)
        else:
            df['forecast_slope'] = 0
            df['forecast_divergence'] = 0
        
        # === Regime Features ===
        if regime is not None:
            # Align indices
            common_idx = df.index.intersection(regime.index)
            df.loc[common_idx, 'regime'] = regime.loc[common_idx, 'regime']
            df.loc[common_idx, 'regime_confidence'] = regime.loc[common_idx, 'regime_confidence']
            df.loc[common_idx, 'regime_suitability'] = regime.loc[common_idx, 'trade_suitability']
            
            # Fill missing
            df['regime'] = df['regime'].fillna(1)  # Default to CYCLICAL
            df['regime_confidence'] = df['regime_confidence'].fillna(0.5)
            df['regime_suitability'] = df['regime_suitability'].fillna(0.5)
        else:
            df['regime'] = 1  # CYCLICAL
            df['regime_confidence'] = 0.5
            df['regime_suitability'] = 0.5
        
        # === Intermarket Pressure ===
        df['intermarket_pressure'] = pressure
        
        # === Composite Risk Score ===
        # Combines volatility, regime, and turning point proximity
        risk_score = pd.Series(1.0, index=df.index)
        
        # Higher volatility = higher risk
        vol_norm = df['volatility'] / df['volatility'].rolling(50).mean()
        risk_score *= (1 + vol_norm.fillna(1))
        
        # Regime adjustment
        regime_risk = df['regime'].map({
            0: 1.5,  # TRENDING - higher risk for cycle trading
            1: 0.8,  # CYCLICAL - lower risk
            2: 2.0,  # VOLATILE - high risk
            3: 0.9,  # COMPRESSED - moderate risk
            4: 1.3   # RESETTING - elevated risk
        })
        risk_score *= regime_risk.fillna(1.0)
        
        # Turning point proximity increases risk (choppy)
        risk_score *= (1 + 0.5 * df['tp_proximity'])
        
        df['risk_score'] = risk_score
        
        # Clean up
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(method='ffill').fillna(0)
        
        return df
    
    def get_feature_summary(self, features: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Get summary statistics for all features across assets.
        
        Args:
            features: Feature dictionary from build_features()
            
        Returns:
            DataFrame with summary statistics
        """
        summary = {}
        
        for symbol, feature_df in features.items():
            summary[symbol] = {
                'avg_amplitude': feature_df['amp_total'].mean(),
                'avg_volatility': feature_df['volatility'].mean(),
                'avg_risk_score': feature_df['risk_score'].mean(),
                'avg_regime_suitability': feature_df['regime_suitability'].mean(),
                'forecast_slope': feature_df['forecast_slope'].iloc[-1] if len(feature_df) > 0 else 0
            }
        
        return pd.DataFrame(summary).T

