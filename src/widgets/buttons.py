"""Custom button widgets with rounded corners and styling.

This module provides enhanced button widgets that integrate with
the application's theme system.
"""

from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

from constants import SURFACE_LIGHT


class RButton(Button):
    """Rounded button with customizable color.
    
    A button widget that renders with rounded corners and supports
    dynamic color changes. The button's background is drawn using
    canvas instructions for better control over appearance.
    
    Attributes:
        _color: Current RGBA color tuple
        _radius: Corner radius in pixels
        _color_instr: Canvas Color instruction for updates
        _bg: Canvas RoundedRectangle instruction
    """
    
    def __init__(self, color: tuple = SURFACE_LIGHT, radius: int = 14, **kwargs):
        """Initialize a rounded button.
        
        Args:
            color: RGBA color tuple (values 0.0-1.0). Defaults to SURFACE_LIGHT
            radius: Corner radius in pixels. Defaults to 14
            **kwargs: Additional keyword arguments passed to Button
        """
        super().__init__(**kwargs)
        
        # Disable default button background
        self.background_normal = self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        
        self._color = color
        self._radius = radius
        
        # Draw custom rounded background
        with self.canvas.before:
            self._color_instr = Color(*color)
            self._bg = RoundedRectangle(radius=[radius])
        
        self.bind(pos=self._update, size=self._update)

    def _update(self, *args) -> None:
        """Update background position and size when widget changes.
        
        This ensures the rounded rectangle stays synchronized with
        the button's position and size.
        """
        self._bg.pos = self.pos
        self._bg.size = self.size

    def set_color(self, color: tuple) -> None:
        """Change the button's background color.
        
        Useful for dynamically changing button appearance based on
        state (e.g., Start button becomes red when timer is running).
        
        Args:
            color: New RGBA color tuple (values 0.0-1.0)
        """
        self._color_instr.rgba = color