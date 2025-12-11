"""Label selection dropdown widget - RESPONSIVE VERSION.

This module provides a custom spinner/dropdown widget for selecting
labels with visual color indicators.
"""

from typing import Callable, Optional
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.dropdown import DropDown
from kivy.graphics import Color, Rectangle, Ellipse

from constants import SURFACE_LIGHT, TEXT
from utils import rh, rp, rs


class LabelSpinner(ButtonBehavior, BoxLayout):
    """Dropdown button for label selection with color indicators.
    
    A custom spinner widget that displays labels with their associated
    colors. When clicked, shows a dropdown menu of all available labels
    in the current group.
    
    Attributes:
        lap: Reference to the lap dictionary (modified in-place)
        lm: LabelManager instance for accessing label data
        on_change: Optional callback function called when label changes
        dropdown: DropDown widget instance
    """
    
    def __init__(self, lap: dict, label_manager, 
                 on_change: Optional[Callable] = None, **kwargs):
        """Initialize the label spinner.
        
        Args:
            lap: Lap dictionary containing 'lbl' key with label data.
                 This is modified in-place when a new label is selected.
            label_manager: LabelManager instance for accessing available labels
            on_change: Optional callback function(label_data) called after
                      a label is selected
            **kwargs: Additional keyword arguments passed to BoxLayout
        """
        super().__init__(**kwargs)
        
        # BoxLayout configuration
        self.spacing = rs()
        self.padding = [rp(), 0]
        self.size_hint_y = None
        self.height = kwargs.get('height', rh('button'))
        
        # Draw background
        with self.canvas.before:
            Color(*SURFACE_LIGHT)
            self.bg_rect = Rectangle()
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        self.lap = lap
        self.lm = label_manager
        self.on_change = on_change
        
        # Create dropdown menu
        self.dropdown = DropDown()
        self._populate_dropdown()
        
        self.bind(on_release=self._on_release)
        self.dropdown.bind(on_select=lambda instance, data: self._select_label(data))
        
        self._update_display()
    
    def _on_release(self, *args) -> None:
        """Handle button click by refreshing and opening dropdown."""
        self._populate_dropdown()
        self.dropdown.open(self)
    
    def _update_bg(self, *args) -> None:
        """Update background rectangle position and size."""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _populate_dropdown(self) -> None:
        """Populate dropdown menu with current label options.
        
        Clears existing options and rebuilds the dropdown with all
        labels from the current group.
        """
        self.dropdown.clear_widgets()
        for label in self.lm.all():
            btn = self._create_option_button(label)
            btn.bind(on_release=lambda btn, lbl=label: self.dropdown.select(lbl))
            self.dropdown.add_widget(btn)

    def _create_option_button(self, label: dict):
        """Create a button widget for a dropdown option.
        
        Args:
            label: Label dictionary with 'name', 'color', and 'is_default' keys
            
        Returns:
            ButtonBehavior + BoxLayout widget configured as an option button
        """
        class OptionButton(ButtonBehavior, BoxLayout):
            """Combined ButtonBehavior and BoxLayout for dropdown options."""
            pass
        
        btn = OptionButton(
            spacing=rs(),
            padding=[rp(), 0],
            size_hint_y=None,
            height=rh('button')
        )
        
        # Draw button background
        with btn.canvas.before:
            Color(*SURFACE_LIGHT)
            btn.bg_rect = Rectangle()
        btn.bind(
            pos=lambda w, *_: setattr(w.bg_rect, 'pos', w.pos),
            size=lambda w, *_: setattr(w.bg_rect, 'size', w.size)
        )
        
        # Add color dot for non-default labels
        if not label["is_default"]:
            dot_size = rp() * 1.5
            dot = Widget(size_hint_x=None, width=rp() * 2.5)
            with dot.canvas:
                Color(*label["color"])
                dot_circle = Ellipse(size=(dot_size, dot_size))
            
            def update_dot_pos(widget, *args):
                dot_circle.pos = (
                    widget.x + widget.width / 2 - dot_size / 2, 
                    widget.y + widget.height / 2 - dot_size / 2
                )
            
            dot.bind(pos=update_dot_pos, size=update_dot_pos)
            btn.add_widget(dot)
        
        # Add label name
        name_label = Label(
            text=label["name"], 
            color=TEXT, 
            halign="left",
            valign="center"
        )
        name_label.bind(size=name_label.setter('text_size'))
        btn.add_widget(name_label)
        
        return btn

    def _update_display(self) -> None:
        """Update the spinner's display with currently selected label.
        
        Clears and rebuilds the spinner's content to show the color
        dot and name of the currently selected label.
        """
        self.clear_widgets()
        
        # Add color dot for non-default labels
        if not self.lap["lbl"]["is_default"]:
            dot_size = rp() * 1.5
            dot = Widget(size_hint_x=None, width=rp() * 2.5)
            with dot.canvas:
                Color(*self.lap["lbl"]["color"])
                display_circle = Ellipse(size=(dot_size, dot_size))
            
            def update_display_dot_pos(widget, *args):
                display_circle.pos = (
                    widget.x + widget.width / 2 - dot_size / 2, 
                    widget.y + widget.height / 2 - dot_size / 2
                )
            
            dot.bind(pos=update_display_dot_pos, size=update_display_dot_pos)
            self.add_widget(dot)
        
        # Add label name
        text_label = Label(
            text=self.lap["lbl"]["name"], 
            color=TEXT, 
            halign="left",
            valign="center"
        )
        text_label.bind(size=text_label.setter('text_size'))
        self.add_widget(text_label)

    def _select_label(self, label_data: dict) -> None:
        """Handle label selection from dropdown.
        
        Updates the lap's label and triggers the on_change callback
        if provided.
        
        Args:
            label_data: Selected label dictionary
        """
        self.lap["lbl"] = label_data.copy()
        self._update_display()
        
        if self.on_change:
            self.on_change(label_data)