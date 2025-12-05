from kivy.uix.colorpicker import ColorPicker
from kivy.uix.slider import Slider


class TouchableSlider(Slider):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cursor_height = 50  # Erhöhe die Höhe des klickbaren Bereichs
    
    def on_touch_down(self, touch):
        return super().on_touch_down(touch)


class CustomColorPicker(ColorPicker):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._replace_sliders()
    
    def _replace_sliders(self):
        """Ersetze alle Slider durch TouchableSlider"""
        def replace_in_widget(widget):
            if isinstance(widget, Slider) and not isinstance(widget, TouchableSlider):
                parent = widget.parent
                if parent:
                    index = parent.children.index(widget)
                    new_slider = TouchableSlider(
                        min=widget.min,
                        max=widget.max,
                        value=widget.value,
                        orientation=widget.orientation,
                        size_hint=widget.size_hint
                    )
                    parent.remove_widget(widget)
                    parent.add_widget(new_slider, index)
            
            if hasattr(widget, 'children'):
                for child in widget.children[:]:
                    replace_in_widget(child)
        
        replace_in_widget(self)