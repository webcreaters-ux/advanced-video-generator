"""
Utility functions and classes for video generator
"""

import os
import sys
import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime


def setup_logging(log_dir: str = "./logs", level: int = logging.INFO) -> logging.Logger:
    """Setup logging configuration
    
    Args:
        log_dir: Directory to store log files
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate log filename
    log_file = os.path.join(
        log_dir, 
        f"video_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


class Timer:
    """Simple timer for measuring execution time"""
    
    def __init__(self):
        """Initialize timer"""
        self._start_time = None
        self._end_time = None
    
    def start(self) -> 'Timer':
        """Start the timer"""
        self._start_time = time.time()
        return self
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time"""
        self._end_time = time.time()
        return self.elapsed()
    
    def elapsed(self) -> float:
        """Get elapsed time in seconds"""
        if self._start_time is None:
            return 0.0
        end = self._end_time or time.time()
        return end - self._start_time
    
    def __enter__(self) -> 'Timer':
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, *args):
        """Context manager exit"""
        self.stop()


class ProgressTracker:
    """Track progress of long-running operations"""
    
    def __init__(self, total_steps: int = 100, description: str = "Processing"):
        """Initialize progress tracker
        
        Args:
            total_steps: Total number of steps
            description: Description of the operation
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self._start_time = time.time()
        self._callbacks = []
    
    def update(self, steps: int = 1, message: Optional[str] = None):
        """Update progress
        
        Args:
            steps: Number of steps to advance
            message: Optional status message
        """
        self.current_step = min(self.current_step + steps, self.total_steps)
        
        # Call callbacks
        for callback in self._callbacks:
            callback(self.get_progress(), message)
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information"""
        elapsed = time.time() - self._start_time
        percentage = (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
        
        # Estimate remaining time
        if self.current_step > 0:
            time_per_step = elapsed / self.current_step
            remaining_steps = self.total_steps - self.current_step
            estimated_remaining = time_per_step * remaining_steps
        else:
            estimated_remaining = 0
        
        return {
            'current': self.current_step,
            'total': self.total_steps,
            'percentage': percentage,
            'elapsed': elapsed,
            'remaining': estimated_remaining,
            'description': self.description
        }
    
    def on_update(self, callback):
        """Register a callback for progress updates"""
        self._callbacks.append(callback)
    
    def complete(self):
        """Mark progress as complete"""
        self.current_step = self.total_steps
        self.update(0, "Complete")


def ensure_dir(path: str) -> str:
    """Ensure a directory exists
    
    Args:
        path: Directory path
        
    Returns:
        The directory path
    """
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(path: str) -> int:
    """Get file size in bytes
    
    Args:
        path: File path
        
    Returns:
        File size in bytes
    """
    if os.path.exists(path):
        return os.path.getsize(path)
    return 0


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_file_size(bytes_size: int) -> str:
    """Format file size in human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} PB"


def clean_filename(filename: str) -> str:
    """Clean a filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()


def split_text(text: str, max_length: int = 200) -> List[str]:
    """Split text into chunks at sentence boundaries
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk
        
    Returns:
        List of text chunks
    """
    chunks = []
    sentences = text.replace('\n', ' ').split('. ')
    
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        if not sentence.endswith('.'):
            sentence += '.'
        
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def estimate_duration(text: str, words_per_minute: int = 150) -> float:
    """Estimate audio duration from text
    
    Args:
        text: Text to estimate
        words_per_minute: Speaking rate
        
    Returns:
        Estimated duration in seconds
    """
    word_count = len(text.split())
    return (word_count / words_per_minute) * 60


class Singleton(type):
    """Singleton metaclass"""
    
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


__all__ = [
    'setup_logging',
    'Timer',
    'ProgressTracker',
    'ensure_dir',
    'get_file_size',
    'format_duration',
    'format_file_size',
    'clean_filename',
    'split_text',
    'estimate_duration',
    'Singleton'
]
