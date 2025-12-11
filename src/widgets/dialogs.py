"""Reusable dialog and popup factory functions - RESPONSIVE VERSION.

This module provides factory functions for creating common dialog types
to avoid code duplication across screens.
"""

from typing import Callable, Optional
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from constants import TEXT, ACCENT, DANGER, SURFACE_LIGHT, PRIMARY
from .buttons import RButton
from utils import rh, rp, rs


def create_text_input_dialog(
    title: str,
    prompt: str,
    initial_text: str = "",
    on_save: Optional[Callable[[str], None]] = None,
    hint_text: str = "",
    save_button_text: str = "Save",
    multiline: bool = False
) -> Popup:
    """Create a dialog with a text input field and save button.
    
    Args:
        title: Dialog window title
        prompt: Instruction text shown above the input field
        initial_text: Pre-filled text in the input field
        on_save: Callback function(text) called when save is pressed
        hint_text: Placeholder text for empty input
        save_button_text: Label for the save button
        multiline: Whether to allow multiple lines of input
        
    Returns:
        Configured Popup instance (not yet opened)
    """
    text_input = TextInput(
        text=initial_text,
        hint_text=hint_text,
        size_hint_y=None,
        height=rh('input'),
        multiline=multiline
    )
    
    save_btn = RButton(
        text=save_button_text,
        color=ACCENT,
        size_hint_y=None,
        height=rh('button')
    )
    
    content = BoxLayout(orientation="vertical", spacing=rs(), padding=rp())
    
    if prompt:
        prompt_label = Label(
            text=prompt,
            color=TEXT,
            size_hint_y=None,
            height=rp() * 2.5
        )
        content.add_widget(prompt_label)
    
    content.add_widget(text_input)
    content.add_widget(save_btn)
    
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.25))
    
    def handle_save(*args):
        if on_save:
            on_save(text_input.text)
        popup.dismiss()
    
    save_btn.bind(on_press=handle_save)
    text_input.bind(on_text_validate=handle_save)
    
    return popup


def create_confirmation_dialog(
    title: str,
    message: str,
    on_confirm: Optional[Callable] = None,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    danger: bool = False
) -> Popup:
    """Create a yes/no confirmation dialog.
    
    Args:
        title: Dialog window title
        message: Confirmation message text
        on_confirm: Callback function called when confirmed
        confirm_text: Label for the confirm button
        cancel_text: Label for the cancel button
        danger: If True, confirm button is styled as dangerous action (red)
        
    Returns:
        Configured Popup instance (not yet opened)
    """
    content = BoxLayout(orientation="vertical", spacing=rs(), padding=rp())
    
    message_label = Label(
        text=message,
        color=TEXT,
        halign="center",
        valign="middle"
    )
    message_label.bind(size=message_label.setter('text_size'))
    content.add_widget(message_label)
    
    # Button container
    buttons = BoxLayout(size_hint_y=None, height=rh('button'), spacing=rs())
    
    cancel_btn = RButton(text=cancel_text, color=SURFACE_LIGHT)
    confirm_btn = RButton(
        text=confirm_text,
        color=DANGER if danger else PRIMARY
    )
    
    buttons.add_widget(cancel_btn)
    buttons.add_widget(confirm_btn)
    content.add_widget(buttons)
    
    popup = Popup(title=title, content=content, size_hint=(0.7, 0.3))
    
    cancel_btn.bind(on_press=popup.dismiss)
    
    def handle_confirm(*args):
        if on_confirm:
            on_confirm()
        popup.dismiss()
    
    confirm_btn.bind(on_press=handle_confirm)
    
    return popup


def create_info_dialog(title: str, message: str, button_text: str = "OK") -> Popup:
    """Create a simple informational dialog with one button.
    
    Args:
        title: Dialog window title
        message: Information message text
        button_text: Label for the dismiss button
        
    Returns:
        Configured Popup instance (not yet opened)
    """
    content = BoxLayout(orientation="vertical", spacing=rs(), padding=rp())
    
    message_label = Label(
        text=message,
        color=TEXT,
        halign="center",
        valign="middle"
    )
    message_label.bind(size=message_label.setter('text_size'))
    content.add_widget(message_label)
    
    ok_btn = RButton(
        text=button_text, 
        color=PRIMARY, 
        size_hint_y=None, 
        height=rh('button')
    )
    content.add_widget(ok_btn)
    
    popup = Popup(title=title, content=content, size_hint=(0.7, 0.25))
    ok_btn.bind(on_press=popup.dismiss)
    
    return popup


def create_two_button_dialog(
    title: str,
    prompt: str,
    input_text: str = "",
    left_button_text: str = "Delete",
    right_button_text: str = "Save",
    on_left: Optional[Callable] = None,
    on_right: Optional[Callable[[str], None]] = None,
    left_danger: bool = True
) -> Popup:
    """Create a dialog with text input and two action buttons.
    
    Useful for edit dialogs that offer both save and delete options.
    
    Args:
        title: Dialog window title
        prompt: Label text above input field
        input_text: Pre-filled text in input
        left_button_text: Label for left button (typically delete)
        right_button_text: Label for right button (typically save)
        on_left: Callback for left button
        on_right: Callback(text) for right button
        left_danger: If True, left button is red (danger style)
        
    Returns:
        Configured Popup instance (not yet opened)
    """
    input_field = TextInput(
        text=input_text,
        size_hint_y=None,
        height=rh('input'),
        multiline=False
    )
    
    buttons = BoxLayout(size_hint_y=None, height=rh('button'), spacing=rs())
    
    left_btn = RButton(
        text=left_button_text,
        color=DANGER if left_danger else SURFACE_LIGHT
    )
    right_btn = RButton(text=right_button_text, color=ACCENT)
    
    buttons.add_widget(left_btn)
    buttons.add_widget(right_btn)
    
    content = BoxLayout(orientation="vertical", spacing=rs(), padding=rp())
    content.add_widget(Label(
        text=prompt,
        color=TEXT,
        size_hint_y=None,
        height=rp() * 2.5
    ))
    content.add_widget(input_field)
    content.add_widget(buttons)
    
    popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
    
    def handle_left(*args):
        popup.dismiss()
        if on_left:
            on_left()
    
    def handle_right(*args):
        if on_right:
            on_right(input_field.text)
        popup.dismiss()
    
    left_btn.bind(on_press=handle_left)
    right_btn.bind(on_press=handle_right)
    input_field.bind(on_text_validate=handle_right)
    
    return popup