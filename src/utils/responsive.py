"""Responsive design utilities for adapting UI to different screen sizes.

This module provides utilities for making the app responsive across
different device sizes, from small phones to tablets and desktops.
"""

from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform


class ResponsiveSize:
    """Helper class for responsive sizing based on screen dimensions.
    
    Provides methods to calculate appropriate sizes for UI elements
    based on the current window size, ensuring the app looks good
    on all screen sizes.
    """
    
    @staticmethod
    def is_mobile() -> bool:
        """Check if running on mobile platform."""
        return platform in ('android', 'ios')
    
    @staticmethod
    def get_header_height() -> float:
        """Get responsive height for header bars."""
        # if ResponsiveSize.is_mobile():
        #     return dp(42)
        return dp(56)
    
    @staticmethod
    def get_button_height() -> float:
        """Get responsive height for standard buttons."""
        if ResponsiveSize.is_mobile():
            return dp(44)  # iOS standard touch target
        return dp(50)
    
    @staticmethod
    def get_large_button_height() -> float:
        """Get responsive height for large action buttons."""
        if ResponsiveSize.is_mobile():
            return dp(52)
        return dp(60)
    
    @staticmethod
    def get_footer_height() -> float:
        """Get responsive height for footer with buttons."""
        if ResponsiveSize.is_mobile():
            # Mobile needs more padding for safe area
            base_height = Window.height * 0.10
            return max(min(base_height, dp(100)), dp(80))
        # Desktop
        base_height = min(Window.height * 0.12, dp(110))
        return max(base_height, dp(90))
    
    @staticmethod
    def get_lap_row_height() -> float:
        """Get responsive height for lap rows."""
        if ResponsiveSize.is_mobile():
            return dp(56)
        return dp(64)
    
    @staticmethod
    def get_label_row_height() -> float:
        """Get responsive height for label management rows."""
        if ResponsiveSize.is_mobile():
            return dp(64)
        return dp(72)
    
    @staticmethod
    def get_time_display_height() -> float:
        """Get responsive height for time display area."""
        if ResponsiveSize.is_mobile():
            # Smaller on mobile
            base_height = Window.height * 0.10
            return max(min(base_height, dp(100)), dp(70))
        # Desktop
        base_height = Window.height * 0.12
        return max(min(base_height, dp(120)), dp(80))
    
    @staticmethod
    def get_provisional_label_height() -> float:
        """Get responsive height for provisional label selector."""
        if ResponsiveSize.is_mobile():
            return dp(72)
        return dp(80)
    
    @staticmethod
    def get_time_font_size() -> str:
        """Get responsive font size for main time display."""
        if ResponsiveSize.is_mobile():
            # Cap maximum size for WQHD displays
            base_size = Window.width * 0.09  # Reduced max
            return f"{base_size}sp"  # Hard cap at sp(22)
        # Desktop
        base_size = min(Window.width * 0.10, sp(42))
        return f"{max(base_size, sp(28))}sp"
    
    @staticmethod
    def get_header_font_size() -> str:
        """Get responsive font size for headers."""
        if ResponsiveSize.is_mobile():
            return f"{min(sp(14), 14)}sp"  # Cap at 14sp for mobile
        return f"{sp(16)}sp"
    
    @staticmethod
    def get_title_font_size() -> str:
        """Get responsive font size for titles."""
        if ResponsiveSize.is_mobile():
            return f"{min(sp(16), 16)}sp"  # Cap at 16sp for mobile
        return f"{sp(20)}sp"
    
    @staticmethod
    def get_button_font_size() -> str:
        """Get responsive font size for buttons."""
        if ResponsiveSize.is_mobile():
            return f"{min(sp(14), 14)}sp"  # Cap at 14sp for mobile
        return f"{sp(16)}sp"
    
    @staticmethod
    def get_icon_font_size() -> str:
        """Get responsive font size for icons."""
        if ResponsiveSize.is_mobile():
            return f"{min(sp(15), 15)}sp"  # Cap at 15sp for mobile
        return f"{sp(18)}sp"
    
    @staticmethod
    def get_padding() -> float:
        """Get responsive padding value."""
        if ResponsiveSize.is_mobile():
            return dp(10)
        return dp(12)
    
    @staticmethod
    def get_spacing() -> float:
        """Get responsive spacing value."""
        if ResponsiveSize.is_mobile():
            return dp(6)
        return dp(8)
    
    @staticmethod
    def get_input_height() -> float:
        """Get responsive height for text inputs."""
        if ResponsiveSize.is_mobile():
            return dp(40)
        return dp(44)
    
    @staticmethod
    def get_popup_size_hint() -> tuple:
        """Get responsive size hint for popups."""
        if ResponsiveSize.is_mobile():
            # Nearly full screen on mobile for better usability
            return (0.95, 0.85)
        # More compact on desktop
        if Window.width < dp(400):
            return (0.95, 0.9)
        return (0.9, 0.85)
    
    @staticmethod
    def get_color_picker_popup_size() -> tuple:
        """Get size hint specifically for color picker popups."""
        if ResponsiveSize.is_mobile():
            # Color picker needs more vertical space
            return (0.95, 0.90)
        return (0.9, 0.88)
    
    @staticmethod
    def get_add_button_size() -> float:
        """Get responsive size for floating add button."""
        if ResponsiveSize.is_mobile():
            return dp(56)  # Material Design standard FAB size
        base_size = min(Window.width * 0.15, dp(72))
        return max(base_size, dp(56))
    
    @staticmethod
    def get_add_button_container_height() -> float:
        """Get responsive height for add button container."""
        button_size = ResponsiveSize.get_add_button_size()
        if ResponsiveSize.is_mobile():
            return button_size + dp(32)
        return button_size + dp(48)
    
    @staticmethod
    def get_slider_height() -> float:
        """Get responsive height for sliders."""
        if ResponsiveSize.is_mobile():
            return dp(48)  # Larger touch target for mobile
        return dp(36)


# Convenience functions for quick access
def rh(key: str) -> float:
    """Get responsive height for a component.
    
    Args:
        key: Component key (header, button, footer, etc.)
        
    Returns:
        Height in pixels
    """
    mapping = {
        'header': ResponsiveSize.get_header_height,
        'button': ResponsiveSize.get_button_height,
        'large_button': ResponsiveSize.get_large_button_height,
        'footer': ResponsiveSize.get_footer_height,
        'lap_row': ResponsiveSize.get_lap_row_height,
        'label_row': ResponsiveSize.get_label_row_height,
        'time_display': ResponsiveSize.get_time_display_height,
        'provisional_label': ResponsiveSize.get_provisional_label_height,
        'input': ResponsiveSize.get_input_height,
        'add_button': ResponsiveSize.get_add_button_size,
        'add_button_container': ResponsiveSize.get_add_button_container_height,
        'slider': ResponsiveSize.get_slider_height,
    }
    
    return mapping.get(key, ResponsiveSize.get_button_height)()


def rfs(key: str) -> str:
    """Get responsive font size for a component.
    
    Args:
        key: Component key (time, header, button, etc.)
        
    Returns:
        Font size as string
    """
    mapping = {
        'time': ResponsiveSize.get_time_font_size,
        'header': ResponsiveSize.get_header_font_size,
        'title': ResponsiveSize.get_title_font_size,
        'button': ResponsiveSize.get_button_font_size,
        'icon': ResponsiveSize.get_icon_font_size,
    }
    
    return mapping.get(key, ResponsiveSize.get_button_font_size)()


def rp() -> float:
    """Get responsive padding.
    
    Returns:
        Padding in pixels
    """
    return ResponsiveSize.get_padding()


def rs() -> float:
    """Get responsive spacing.
    
    Returns:
        Spacing in pixels
    """
    return ResponsiveSize.get_spacing()