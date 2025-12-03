"""
File Manager for Meridian v2.1.2

Safe file operations with atomic writes.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, Any
import json
import gzip


class FileManager:
    """
    Safe file operations manager.
    
    Features:
    - Atomic writes (write to temp, then move)
    - Directory creation
    - Compressed writes (optional)
    - Safe cleanup
    """
    
    @staticmethod
    def safe_write(
        path: Union[str, Path],
        content: Union[str, bytes],
        compress: bool = False
    ) -> Path:
        """
        Write content to file atomically.
        
        Args:
            path: Target file path
            content: Content to write
            compress: Whether to gzip compress
        
        Returns:
            Path to written file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file first
        # Always use binary mode if compressing
        mode = 'wb' if (compress or isinstance(content, bytes)) else 'w'
        
        with tempfile.NamedTemporaryFile(
            mode=mode,
            dir=path.parent,
            delete=False
        ) as tmp:
            tmp_path = Path(tmp.name)
            
            if compress:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                tmp.write(gzip.compress(content))
            else:
                tmp.write(content)
        
        # Atomic move
        shutil.move(str(tmp_path), str(path))
        
        return path
    
    @staticmethod
    def safe_read(
        path: Union[str, Path],
        compressed: bool = False,
        binary: bool = False
    ) -> Union[str, bytes]:
        """
        Read file safely.
        
        Args:
            path: File path
            compressed: Whether file is gzipped
            binary: Return bytes instead of str
        
        Returns:
            File content
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        if compressed:
            with gzip.open(path, 'rb') as f:
                content = f.read()
                if not binary:
                    content = content.decode('utf-8')
        else:
            mode = 'rb' if binary else 'r'
            with open(path, mode) as f:
                content = f.read()
        
        return content
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """
        Ensure directory exists.
        
        Args:
            path: Directory path
        
        Returns:
            Path object
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def clean_old_files(
        directory: Union[str, Path],
        pattern: str = "*",
        keep_recent: int = 100
    ) -> int:
        """
        Clean old files from directory.
        
        Args:
            directory: Directory to clean
            pattern: File pattern to match
            keep_recent: Number of recent files to keep
        
        Returns:
            Number of files deleted
        """
        directory = Path(directory)
        
        if not directory.exists():
            return 0
        
        # Get matching files sorted by modification time
        files = sorted(
            directory.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Delete old files
        deleted = 0
        for file in files[keep_recent:]:
            try:
                file.unlink()
                deleted += 1
            except:
                pass
        
        return deleted


def safe_write(path: Union[str, Path], content: Any, **kwargs) -> Path:
    """Convenience function for safe write"""
    return FileManager.safe_write(path, content, **kwargs)


def safe_read(path: Union[str, Path], **kwargs) -> Any:
    """Convenience function for safe read"""
    return FileManager.safe_read(path, **kwargs)

