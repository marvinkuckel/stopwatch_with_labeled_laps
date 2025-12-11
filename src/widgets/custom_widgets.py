"""Custom widgets optimized for mobile touch interaction."""

from kivy.uix.colorpicker import ColorPicker
from kivy.uix.slider import Slider
from kivy.utils import platform


class TouchableSlider(Slider):
    """Enhanced slider with better touch interaction for mobile."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Much larger touch area for mobile
        if platform in ('android', 'ios'):
            self.cursor_height = 48
            self.cursor_width = 48
            self.padding = 24  # Extra padding around slider
        else:
            self.cursor_height = 32
            self.cursor_width = 32
    
    def on_touch_down(self, touch):
        """Override to expand touch detection area."""
        # Check if touch is near the slider (expanded hitbox)
        if self.orientation == 'horizontal':
            # Expand vertical touch area
            if (self.x <= touch.x <= self.right and 
                self.y - 20 <= touch.y <= self.top + 20):
                touch.grab(self)
                # Jump to touch position
                if self.width > 0:
                    self.value_pos = touch.x
                return True
        else:
            # Expand horizontal touch area
            if (self.y <= touch.y <= self.top and
                self.x - 20 <= touch.x <= self.right + 20):
                touch.grab(self)
                # Jump to touch position
                if self.height > 0:
                    self.value_pos = touch.y
                return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch move with grabbed touch."""
        if touch.grab_current is self:
            if self.orientation == 'horizontal':
                if self.width > 0:
                    self.value_pos = touch.x
            else:
                if self.height > 0:
                    self.value_pos = touch.y
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch release."""
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


# Simple wrapper that just adjusts ColorPicker size for mobile
def create_mobile_color_picker(**kwargs):
    """Factory function to create a color picker optimized for mobile.
    
    Returns:
        Standard ColorPicker with mobile-friendly sizing
    """
    picker = ColorPicker(**kwargs)
    
    # Mobile optimizations - just adjust sizes
    if platform in ('android', 'ios'):
        # These are the only safe changes we can make
        picker.font_name = 'Roboto'  # Standard Android font
        picker.font_size = '15sp'
    
    return picker