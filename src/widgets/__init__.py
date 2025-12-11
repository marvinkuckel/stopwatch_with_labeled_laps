"""Custom UI widgets and components for the Stopwatch application.

This package contains:
- Custom button widgets (RButton)
- Label selection spinners (LabelSpinner)
- Slide-in menus (SlideMenu)
- Reusable dialog factories
"""

from .buttons import RButton
from .spinners import LabelSpinner
from .menus import SlideMenu
from .dialogs import (
    create_text_input_dialog,
    create_confirmation_dialog,
    create_info_dialog,
    create_two_button_dialog
)
from .custom_widgets import (
    TouchableSlider,
    create_mobile_color_picker
)
from .slider_patch import (
    _patched_slider_init,
    _patched_on_touch_down,
    _patched_on_touch_move,
    apply_slider_patches
)

__all__ = [
    'RButton',
    'LabelSpinner',
    'SlideMenu',
    'create_text_input_dialog',
    'create_confirmation_dialog',
    'create_info_dialog',
    'create_two_button_dialog',
    'TouchableSlider',
    'create_mobile_color_picker',
    '_patched_slider_init',
    '_patched_on_touch_down',
    '_patched_on_touch_move',
    'apply_slider_patches'
]