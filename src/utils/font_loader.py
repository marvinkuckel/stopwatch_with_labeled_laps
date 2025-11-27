"""Font loading utilities for the Stopwatch application.

This module handles downloading and registering custom fonts,
specifically Font Awesome icons used throughout the UI.
"""

import os
import urllib.request
from kivy.core.text import LabelBase

from constants import ICON_FONT, ICON_FONT_FILE, ICON_FONT_URL


def download_font_awesome() -> bool:
    """Download and register the Font Awesome font.
    
    This function performs two operations:
    1. Downloads the Font Awesome TTF file from CDN if not already present
    2. Registers the font with Kivy's text rendering system
    
    The font is downloaded to the current working directory and registered
    under the name defined in constants.ICON_FONT.
    
    Returns:
        True if font was successfully loaded/registered, False on error
        
    Note:
        If the font file already exists locally, it skips the download
        and proceeds directly to registration.
    """
    # Check if font file already exists
    if not os.path.exists(ICON_FONT_FILE):
        print("📦 Downloading Font Awesome...")
        
        try:
            urllib.request.urlretrieve(ICON_FONT_URL, ICON_FONT_FILE)
            print("✅ Font Awesome downloaded successfully!")
        except Exception as e:
            print(f"❌ Error downloading font: {e}")
            return False
    
    # Register the font with Kivy
    try:
        LabelBase.register(name=ICON_FONT, fn_regular=ICON_FONT_FILE)
        print("✅ Font Awesome loaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Error loading font: {e}")
        return False