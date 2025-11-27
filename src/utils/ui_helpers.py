"""UI helper functions for window management and layout.

This module contains utility functions for managing window properties
and ensuring consistent UI behavior across different screen sizes.
"""

from constants import ASPECT_RATIO


def enforce_aspect_ratio(window, width: int, height: int) -> None:
    """Maintain a fixed aspect ratio when the window is resized.
    
    This function is typically bound to the window's on_resize event
    to ensure the application maintains its intended aspect ratio
    regardless of how the user attempts to resize the window.
    
    The function adjusts either width or height (whichever results in
    a smaller window) to match the target aspect ratio defined in constants.
    
    Args:
        window: Kivy Window instance (not used directly, but required by event)
        width: Requested window width in pixels
        height: Requested window height in pixels
        
    Note:
        This function modifies window.size as a side effect.
    """
    # Determine which dimension to constrain based on aspect ratio
    if width / height > ASPECT_RATIO:
        # Width is too large, constrain it
        width = int(height * ASPECT_RATIO)
    else:
        # Height is too large, constrain it
        height = int(width / ASPECT_RATIO)
    
    window.size = (width, height)