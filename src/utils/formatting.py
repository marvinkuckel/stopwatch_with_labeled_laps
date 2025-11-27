"""Time formatting utilities for the Stopwatch application.

This module provides functions for converting raw time values into
human-readable string formats suitable for display in the UI.
"""


def format_time(seconds: float) -> str:
    """Convert seconds to a formatted time string.
    
    Formats time in the pattern "M:SS.mmm" where:
    - M = minutes (no leading zero)
    - SS = seconds (always 2 digits)
    - mmm = milliseconds (always 3 digits)
    
    Args:
        seconds: Time value in seconds (can include fractional seconds)
        
    Returns:
        Formatted time string, e.g. "1:23.456" or "0:05.789"
        
    Examples:
        >>> format_time(83.456)
        '1:23.456'
        >>> format_time(5.789)
        '0:05.789'
        >>> format_time(0.123)
        '0:00.123'
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{minutes}:{secs:02d}.{millis:03d}"