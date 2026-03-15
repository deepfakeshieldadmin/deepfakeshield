"""
General utility functions for DeepFake Shield.
"""
import os
import uuid
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_unique_filename(original_filename, prefix=''):
    """Generate a unique filename preserving the original extension."""
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:12]
    safe_prefix = prefix.replace(' ', '_')[:20] if prefix else 'file'
    return f"{safe_prefix}_{unique_id}{ext}"


def get_file_size_display(size_bytes):
    """Convert bytes to human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def clamp(value, min_val=0.0, max_val=100.0):
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, float(value)))


def safe_division(numerator, denominator, default=0.0):
    """Safe division that returns default on zero division."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def cleanup_old_files(directory, max_age_hours=24):
    """Remove files older than max_age_hours from a directory."""
    import time
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return
        cutoff = time.time() - (max_age_hours * 3600)
        for f in dir_path.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                logger.debug(f"Cleaned up old file: {f.name}")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")