"""
Unified Serializer for Meridian v2.1.2

Consistent serialization for all data types.
"""

import json
import pickle
from pathlib import Path
from typing import Any, Union
from dataclasses import asdict, is_dataclass
import pandas as pd
import numpy as np


class Serializer:
    """
    Unified serialization handler.
    
    Supports:
    - DataFrames → parquet
    - NumPy → binary
    - Dataclasses → dict
    - General objects → JSON/pickle
    """
    
    @staticmethod
    def serialize(obj: Any, fmt: str = 'auto') -> bytes:
        """
        Serialize object to bytes.
        
        Args:
            obj: Object to serialize
            fmt: Format ('auto', 'json', 'pickle', 'parquet', 'numpy')
        
        Returns:
            Serialized bytes
        """
        if fmt == 'auto':
            fmt = Serializer._detect_format(obj)
        
        if fmt == 'json':
            json_str = Serializer._to_json(obj)
            return json_str.encode('utf-8')
        
        elif fmt == 'pickle':
            return pickle.dumps(obj)
        
        elif fmt == 'numpy':
            if not isinstance(obj, np.ndarray):
                raise TypeError("Object must be numpy array for 'numpy' format")
            import io
            buffer = io.BytesIO()
            np.save(buffer, obj)
            return buffer.getvalue()
        
        else:
            # Default to pickle
            return pickle.dumps(obj)
    
    @staticmethod
    def deserialize(data: bytes, fmt: str = 'auto') -> Any:
        """
        Deserialize bytes to object.
        
        Args:
            data: Serialized bytes
            fmt: Format hint
        
        Returns:
            Deserialized object
        """
        if fmt == 'json':
            json_str = data.decode('utf-8')
            return json.loads(json_str)
        
        elif fmt == 'numpy':
            import io
            buffer = io.BytesIO(data)
            return np.load(buffer)
        
        else:
            # Try pickle
            return pickle.loads(data)
    
    @staticmethod
    def _detect_format(obj: Any) -> str:
        """Detect appropriate format for object"""
        if isinstance(obj, pd.DataFrame):
            return 'parquet'
        elif isinstance(obj, np.ndarray):
            return 'numpy'
        elif isinstance(obj, (dict, list, str, int, float, bool, type(None))):
            return 'json'
        elif is_dataclass(obj):
            return 'json'
        else:
            return 'pickle'
    
    @staticmethod
    def _to_json(obj: Any) -> str:
        """Convert object to JSON string"""
        if is_dataclass(obj):
            obj = asdict(obj)
        
        return json.dumps(obj, indent=2, default=str)


# DataFrame-specific functions

def save_dataframe(
    df: pd.DataFrame,
    path: Union[str, Path],
    compress: bool = True
) -> Path:
    """
    Save DataFrame to parquet (or pickle if parquet unavailable).
    
    Args:
        df: DataFrame
        path: Target path
        compress: Whether to compress
    
    Returns:
        Path to saved file
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try parquet first
        compression = 'gzip' if compress else None
        df.to_parquet(path, compression=compression)
    except ImportError:
        # Fall back to pickle if parquet engines not available
        if compress:
            import gzip
            with gzip.open(path, 'wb') as f:
                df.to_pickle(f)
        else:
            df.to_pickle(path)
    
    return path


def load_dataframe(path: Union[str, Path]) -> pd.DataFrame:
    """
    Load DataFrame from parquet or pickle.
    
    Args:
        path: File path
    
    Returns:
        DataFrame
    """
    path = Path(path)
    
    try:
        # Try parquet first
        return pd.read_parquet(path)
    except (ImportError, Exception):
        # Fall back to pickle
        # Try to detect if compressed
        import gzip
        
        # Try compressed first
        try:
            with gzip.open(path, 'rb') as f:
                return pd.read_pickle(f)
        except (OSError, gzip.BadGzipFile):
            # Not compressed, try regular pickle
            return pd.read_pickle(path)


# General functions

def serialize(obj: Any, fmt: str = 'auto') -> bytes:
    """Serialize object"""
    return Serializer.serialize(obj, fmt)


def deserialize(data: bytes, fmt: str = 'auto') -> Any:
    """Deserialize object"""
    return Serializer.deserialize(data, fmt)

