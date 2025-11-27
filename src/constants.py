"""Application-wide constants for the Stopwatch app.

This module contains all configuration values including:
- Display settings (resolution, aspect ratio)
- Theme colors (primary, accent, surface, text colors)
- Font Awesome icon unicode characters
- Font configuration

All colors are defined as RGBA tuples with values from 0.0 to 1.0.
"""

# ============================================================================
# Display Configuration
# ============================================================================

ASPECT_RATIO = 9 / 16
"""float: Target aspect ratio for the application window (9:16 portrait)."""

DESKTOP_RESOLUTION = (545, 968)
"""tuple[int, int]: Default window resolution for desktop platforms."""


# ============================================================================
# Theme Colors (RGBA format: 0.0 to 1.0)
# ============================================================================

PRIMARY = (0.25, 0.5, 0.9, 1)
"""tuple: Primary brand color - blue."""

ACCENT = (0.2, 0.7, 0.3, 1)
"""tuple: Accent color for positive actions - green."""

DANGER = (0.8, 0.25, 0.25, 1)
"""tuple: Danger color for destructive actions - red."""

SURFACE = (0.16, 0.16, 0.16, 1)
"""tuple: Dark surface background color."""

SURFACE_LIGHT = (0.22, 0.22, 0.22, 1)
"""tuple: Lighter surface color for elevated elements."""

TEXT = (0.92, 0.92, 0.92, 1)
"""tuple: Primary text color - near white."""

MUTED = (0.7, 0.7, 0.7, 1)
"""tuple: Muted text color for secondary information."""


# ============================================================================
# Font Awesome Icons (Font Awesome 6 Solid)
# ============================================================================

ICON_GEAR = "\uf013"
"""str: Settings/gear icon."""

ICON_TAGS = "\uf02c"
"""str: Tags/labels icon."""

ICON_ARROW_LEFT = "\uf060"
"""str: Left arrow for back navigation."""

ICON_PEN = "\uf304"
"""str: Pen/edit icon."""

ICON_PLUS = "\u002b"
"""str: Plus sign for adding items."""

ICON_BARS = "\uf0c9"
"""str: Hamburger menu icon."""

ICON_TRASH = "\uf1f8"
"""str: Trash/delete icon."""

ICON_FOLDER_PLUS = "\uf65e"
"""str: Folder with plus sign."""

ICON_PLAY = "\uf04b"
"""str: Play/start icon."""

ICON_STOP = "\uf04d"
"""str: Stop icon."""

ICON_CLOCK = "\uf017"
"""str: Clock icon for time display."""

ICON_CALENDAR = "\uf073"
"""str: Calendar icon for dates."""

ICON_FLAG_CHECKERED = "\uf11e"
"""str: Checkered flag icon for laps/finish."""


# ============================================================================
# Font Configuration
# ============================================================================

ICON_FONT = 'Icons'
"""str: Registered font name for Font Awesome icons."""

ICON_FONT_FILE = 'fa-solid-900.ttf'
"""str: Filename of the Font Awesome font file."""

ICON_FONT_URL = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.ttf"
"""str: CDN URL for downloading Font Awesome if not present locally."""