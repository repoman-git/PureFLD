"""
Unit Tests for Data Integrity Enforcement

Tests the year-2000 rule and minimum bar requirements.

Author: Meridian Team
Date: December 4, 2025
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

import pandas as pd
import datetime as dt
import pytest
from meridian_v2_1_2.utils.data_validation import minimum_history_required
from meridian_v2_1_2.runtime.data_integrity_enforcer import data_integrity


class TestDataValidationDecorator:
    """Test the @minimum_history_required decorator"""
    
    def test_decorator_rejects_short_history(self):
        """Decorator should reject data starting after 2000"""
        # Data starting in 2010 (too recent)
        idx = pd.date_range(start="2010-01-01", periods=1000, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        @minimum_history_required(start_year=2000, min_bars=1500)
        def dummy_function(price_df):
            return True
        
        with pytest.raises(ValueError) as exc_info:
            dummy_function(df)
        
        assert "DATA INTEGRITY VIOLATION" in str(exc_info.value)
        assert "2010" in str(exc_info.value)
    
    def test_decorator_accepts_valid_history(self):
        """Decorator should accept data from ≥2000"""
        # Data from 1995 (valid)
        idx = pd.date_range(start="1995-01-01", periods=2000, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        @minimum_history_required(start_year=2000, min_bars=1500)
        def dummy_function(price_df):
            return True
        
        result = dummy_function(df)
        assert result is True
    
    def test_decorator_rejects_insufficient_bars(self):
        """Decorator should reject datasets with too few bars"""
        # Valid start date but too few bars
        idx = pd.date_range(start="1990-01-01", periods=500, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        @minimum_history_required(start_year=2000, min_bars=1500)
        def dummy_function(price_df):
            return True
        
        with pytest.raises(ValueError) as exc_info:
            dummy_function(df)
        
        assert "500" in str(exc_info.value)
        assert "1500" in str(exc_info.value)


class TestRuntimeEnforcer:
    """Test the DataIntegrityEnforcer runtime validator"""
    
    def test_runtime_rejects_short_start_date(self):
        """Runtime validator should reject recent start dates"""
        idx = pd.date_range(start="2015-01-01", periods=2000, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        with pytest.raises(ValueError) as exc_info:
            data_integrity.validate(df, module="phasing", symbol="TEST")
        
        assert "DATA INTEGRITY VIOLATION" in str(exc_info.value)
        assert "2015" in str(exc_info.value)
    
    def test_runtime_rejects_insufficient_bars(self):
        """Runtime validator should reject insufficient bar counts"""
        # Valid start date but too few bars for backtest
        idx = pd.date_range(start="1995-01-01", periods=200, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        with pytest.raises(ValueError) as exc_info:
            data_integrity.validate(df, module="backtest", symbol="TEST")
        
        assert "200" in str(exc_info.value)
        assert "2500" in str(exc_info.value)
    
    def test_runtime_accepts_valid_data(self):
        """Runtime validator should accept valid data"""
        # Long history, sufficient bars
        idx = pd.date_range(start="1990-01-01", periods=3000, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        result = data_integrity.validate(df, module="intermarket", symbol="GLD")
        assert result is True
    
    def test_runtime_checks_all_modules(self):
        """Verify all module types have requirements"""
        idx = pd.date_range(start="1995-01-01", periods=3000, freq="D")
        df = pd.DataFrame({"close": range(len(idx))}, index=idx)
        
        # All these should pass
        for module in ['regime', 'volatility', 'phasing', 'harmonics',
                      'forecast', 'intermarket', 'backtest']:
            result = data_integrity.validate(df, module=module)
            assert result is True


class TestDataQuality:
    """Test data quality checks"""
    
    def test_detect_nan_values(self):
        """Should detect NaN values"""
        from meridian_v2_1_2.utils.data_validation import validate_data_quality
        
        idx = pd.date_range("2000-01-01", periods=100)
        data = pd.Series(range(100), index=idx)
        data.iloc[50] = None  # Insert NaN
        
        is_valid, issues = validate_data_quality(data, "TEST")
        assert not is_valid
        assert any("NaN" in issue for issue in issues)
    
    def test_detect_duplicates(self):
        """Should detect duplicate timestamps"""
        from meridian_v2_1_2.utils.data_validation import validate_data_quality
        
        idx = pd.DatetimeIndex(['2000-01-01', '2000-01-02', '2000-01-02', '2000-01-03'])
        data = pd.Series([1, 2, 3, 4], index=idx)
        
        is_valid, issues = validate_data_quality(data, "TEST")
        assert not is_valid
        assert any("duplicate" in issue for issue in issues)
    
    def test_accept_clean_data(self):
        """Should accept clean, valid data"""
        from meridian_v2_1_2.utils.data_validation import validate_data_quality
        
        idx = pd.date_range("2000-01-01", periods=1000)
        data = pd.Series(range(1000), index=idx)
        
        is_valid, issues = validate_data_quality(data, "TEST")
        assert is_valid
        assert len(issues) == 0


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

