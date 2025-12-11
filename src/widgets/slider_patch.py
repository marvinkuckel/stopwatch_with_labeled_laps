"""Patch Kivy Slider for better mobile touch interaction.

This module monkey-patches the Slider class to have larger touch areas
on mobile platforms. Call apply_slider_patches() at app startup.
"""

from kivy.uix.slider import Slider
from kivy.utils import platform


# Store original methods
_original_slider_init = Slider.__init__
_original_slider_on_touch_down = Slider.on_touch_down
_original_slider_on_touch_move = Slider.on_touch_move


def _patched_slider_init(self, **kwargs):
    """Patched __init__ with larger touch areas for mobile."""
    _original_slider_init(self, **kwargs)
    
    if platform in ('android', 'ios'):
        # Much larger cursor for mobile
        self.cursor_height = 48
        self.cursor_width = 48
        self.padding = 16
    

def _patched_on_touch_down(self, touch):
    """Patched touch down with expanded hit area."""
    # Expand touch detection area for mobile
    if platform in ('android', 'ios'):
        if self.orientation == 'horizontal':
            # Expand vertical touch area by 30px
            if (self.x <= touch.x <= self.right and 
                self.y - 30 <= touch.y <= self.top + 30):
                # Force it to register as a hit
                touch.grab(self)
                if self.width > 0:
                    self.value_pos = touch.x
                return True
        else:
            # Expand horizontal touch area by 30px
            if (self.y <= touch.y <= self.top and
                self.x - 30 <= touch.x <= self.right + 30):
                touch.grab(self)
                if self.height > 0:
                    self.value_pos = touch.y
                return True
    
    # Fall back to original behavior
    return _original_slider_on_touch_down(self, touch)


def _patched_on_touch_move(self, touch):
    """Patched touch move to work with grabbed touches."""
    if touch.grab_current is self:
        # We grabbed this touch, update value
        if self.orientation == 'horizontal':
            if self.width > 0:
                self.value_pos = touch.x
        else:
            if self.height > 0:
                self.value_pos = touch.y
        return True
    
    return _original_slider_on_touch_move(self, touch)


def apply_slider_patches():
    """Apply all slider patches for better mobile interaction.
    
    Call this function once at app startup, before building any UI.
    
    Example:
        from slider_patch import apply_slider_patches
        
        class MyApp(App):
            def build(self):
                apply_slider_patches()  # Apply patches first
                return build_ui()
    """
    if platform in ('android', 'ios'):
        print("🔧 Applying mobile slider patches...")
        Slider.__init__ = _patched_slider_init
        Slider.on_touch_down = _patched_on_touch_down
        Slider.on_touch_move = _patched_on_touch_move
        print("✅ Slider patches applied")
    else:
        print("ℹ️ Desktop platform - slider patches not needed")