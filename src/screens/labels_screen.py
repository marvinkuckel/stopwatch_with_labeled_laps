"""Labels management screen for organizing and editing labels.

This module provides the interface for:
- Creating and editing labels
- Managing label groups
- Configuring label properties (name, color, description, auto-start/stop)
- Organizing labels by groups for different activities
"""

from typing import Optional
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle

from constants import (ACCENT, DANGER, ICON_ARROW_LEFT, ICON_FOLDER_PLUS,
                      ICON_FONT, ICON_PEN, ICON_PLUS, ICON_TAGS, ICON_TRASH,
                      MUTED, PRIMARY, SURFACE_LIGHT, TEXT)
from widgets import RButton, create_info_dialog, create_two_button_dialog, create_confirmation_dialog
#from widgets.custom_widgets import CustomColorPicker as ColorPicker


class LabelsScreen(Screen):
    """Screen for managing labels and label groups.
    
    Provides a comprehensive interface for organizing labels:
    - Create/edit/delete individual labels
    - Manage label groups for different activities
    - Configure label colors and descriptions
    - Set up auto-start/stop functionality
    
    Attributes:
        lm: LabelManager instance
        timer_screen: Reference to TimerScreen for updating laps
        grid: GridLayout containing label rows
        group_spinner: Spinner for selecting active group
    """
    
    def __init__(self, lm, **kwargs):
        """Initialize the labels screen.
        
        Args:
            lm: LabelManager instance
            **kwargs: Additional keyword arguments passed to Screen
        """
        super().__init__(**kwargs)
        self.lm = lm
        self.timer_screen: Optional[Screen] = None
        self._build_ui()

    # ==========================================================================
    # UI CONSTRUCTION
    # ==========================================================================

    def _build_ui(self) -> None:
        """Build the complete user interface."""
        root = BoxLayout(orientation="vertical")
        
        root.add_widget(self._create_header())
        root.add_widget(self._create_label_list())
        root.add_widget(self._create_add_button())
        
        self.add_widget(root)
        self._update_labels()

    def _create_header(self) -> BoxLayout:
        """Create header with back button and group management.
        
        Returns:
            BoxLayout containing header widgets
        """
        header = BoxLayout(size_hint_y=None, height=56, padding=8, spacing=8)
        
        # Background
        with header.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            header.bg = Rectangle()
        header.bind(
            pos=lambda *_: setattr(header.bg, 'pos', header.pos),
            size=lambda *_: setattr(header.bg, 'size', header.size)
        )
        
        # Back button
        back_btn = RButton(
            text=ICON_ARROW_LEFT,
            color=SURFACE_LIGHT,
            size_hint_x=None,
            width=50,
            font_name=ICON_FONT,
            font_size="22sp"
        )
        back_btn.bind(on_press=self._navigate_back)
        
        # Title
        title = Label(
            text="Manage Labels",
            color=TEXT,
            font_size="18sp",
            size_hint_x=None,
            width=140
        )
        
        # Group controls (spinner + edit + add buttons)
        group_controls = self._create_group_controls()
        
        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(Widget())  # Spacer
        header.add_widget(group_controls)
        
        return header

    def _create_group_controls(self) -> BoxLayout:
        """Create the group selector with edit and add buttons.
        
        Returns:
            BoxLayout containing spinner and buttons as a unified component
        """
        group_controls = BoxLayout(
            spacing=0,
            size_hint_x=None,
            width=210,
            padding=0
        )
        
        # Unified background
        with group_controls.canvas.before:
            Color(*SURFACE_LIGHT)
            group_controls.bg = RoundedRectangle(radius=[12])
        group_controls.bind(
            pos=lambda w, *_: setattr(w.bg, 'pos', w.pos),
            size=lambda w, *_: setattr(w.bg, 'size', w.size)
        )
        
        # Group spinner
        self.group_spinner = Spinner(
            text=self.lm.group,
            values=list(self.lm.groups.keys()),
            background_color=(0, 0, 0, 0),
            background_normal='',
            background_down='',
            padding=[12, 0]
        )
        self.group_spinner.bind(text=self._change_group)
        
        # Separator before edit button
        separator1 = self._create_separator()
        
        # Edit group button
        edit_group_btn = RButton(
            text=ICON_PEN,
            color=(0, 0, 0, 0),
            size_hint_x=None,
            width=44,
            font_name=ICON_FONT,
            font_size="16sp"
        )
        edit_group_btn.bind(on_press=self._open_edit_group_popup)
        
        # Separator before add button
        separator2 = self._create_separator()
        
        # Add group button
        add_group_btn = RButton(
            text=ICON_FOLDER_PLUS,
            color=(0, 0, 0, 0),
            size_hint_x=None,
            width=44,
            font_name=ICON_FONT,
            font_size="17sp"
        )
        add_group_btn.bind(on_press=self._open_add_group_popup)
        
        group_controls.add_widget(self.group_spinner)
        group_controls.add_widget(separator1)
        group_controls.add_widget(edit_group_btn)
        group_controls.add_widget(separator2)
        group_controls.add_widget(add_group_btn)
        
        return group_controls

    def _create_separator(self) -> Widget:
        """Create a vertical separator line.
        
        Returns:
            Widget with vertical line drawn
        """
        separator = Widget(size_hint_x=None, width=1)
        with separator.canvas.before:
            Color(0.28, 0.28, 0.28, 1)
            separator.line = Rectangle()
        separator.bind(
            pos=lambda w, *_: setattr(w.line, 'pos', w.pos),
            size=lambda w, *_: setattr(w.line, 'size', w.size)
        )
        return separator

    def _create_label_list(self) -> ScrollView:
        """Create scrollable list of labels.
        
        Returns:
            ScrollView containing label grid
        """
        scroll = ScrollView()
        
        self.grid = GridLayout(
            cols=1,
            spacing=12,
            size_hint_y=None,
            padding=[12, 0]
        )
        self.grid.bind(minimum_height=self.grid.setter("height"))
        
        scroll.add_widget(self.grid)
        
        return scroll

    def _create_add_button(self) -> BoxLayout:
        """Create the floating add button for new labels.
        
        Returns:
            BoxLayout containing centered add button
        """
        plus_btn = RButton(
            text=ICON_PLUS,
            color=PRIMARY,
            size_hint=(None, None),
            width=72,
            height=72,
            font_name=ICON_FONT,
            font_size="36sp"
        )
        plus_btn.bind(on_press=self._open_add_label_popup)
        
        container = BoxLayout(size_hint_y=None, height=120, padding=20)
        container.add_widget(Widget())
        container.add_widget(plus_btn)
        container.add_widget(Widget())
        
        return container

    # ==========================================================================
    # LABEL DISPLAY
    # ==========================================================================

    def _update_labels(self) -> None:
        """Refresh the display of all labels in current group."""
        self.grid.clear_widgets()
        
        for i, label in enumerate(self.lm.all()):
            row = self._create_label_row(i, label)
            self.grid.add_widget(row)

    def _create_label_row(self, index: int, label: dict) -> BoxLayout:
        """Create a row displaying a label with edit/delete buttons.
        
        Args:
            index: Index of label in current group
            label: Label dictionary
            
        Returns:
            BoxLayout containing label information and controls
        """
        row = BoxLayout(size_hint_y=None, height=72, padding=12, spacing=12)
        
        # Color indicator
        color_box = Widget(size_hint_x=None, width=56)
        with color_box.canvas:
            Color(*label["color"])
            color_box.circle = Ellipse(size=(36, 36))
        
        def update_circle_pos(w, *_):
            w.circle.pos = (
                w.x + w.width / 2 - 18,
                w.y + w.height / 2 - 18
            )
        
        color_box.bind(pos=update_circle_pos, size=update_circle_pos)
        
        # Label name
        name_label = Label(
            text=label["name"],
            color=TEXT,
            font_size="17sp",
            halign="left",
            valign="middle"
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        # Description
        desc_label = Label(
            text=label.get("desc", ""),
            color=MUTED,
            size_hint_x=0.3,
            halign="left",
            valign="middle"
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        # Edit button (disabled for default label)
        if not label.get("is_default", False):
            edit_btn = RButton(
                text=ICON_PEN,
                color=PRIMARY,
                size_hint_x=None,
                width=50,
                font_name=ICON_FONT,
                font_size="18sp"
            )
            edit_btn.bind(on_press=lambda _, i=index: self._open_edit_label_popup(i))
        else:
            edit_btn = Widget(size_hint_x=None, width=50)
        
        # Delete button (disabled for default label)
        if not label.get("is_default", False):
            del_btn = RButton(
                text=ICON_TRASH,
                color=DANGER,
                size_hint_x=None,
                width=50,
                font_name=ICON_FONT,
                font_size="18sp"
            )
            del_btn.bind(on_press=lambda _, i=index: self._delete_label(i))
        else:
            del_btn = Widget(size_hint_x=None, width=50)
        
        row.add_widget(color_box)
        row.add_widget(name_label)
        row.add_widget(desc_label)
        row.add_widget(edit_btn)
        row.add_widget(del_btn)
        
        return row

    # ==========================================================================
    # LABEL OPERATIONS
    # ==========================================================================

    def _delete_label(self, index: int) -> None:
        """Delete a label from the current group.
        
        Args:
            index: Index of label to delete
        """
        label = self.lm.groups[self.lm.group][index]
        
        # Cannot delete default label
        if not label.get("is_default", False):
            del self.lm.groups[self.lm.group][index]
            self.lm.idx = 0
            self._update_labels()
            self.lm.save()

    def _open_add_label_popup(self, *args) -> None:
        """Open popup for creating a new label."""
        name_input = TextInput(
            hint_text="Label Name",
            size_hint_y=None,
            height=40
        )
        desc_input = TextInput(
            hint_text="Description (optional)",
            size_hint_y=None,
            height=40
        )
        
        color_picker = ColorPicker()
        
        # Auto start/stop checkbox
        checkbox_container = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=12,
            padding=[0, 8]
        )
        auto_check = CheckBox(size_hint_x=None, width=40)
        checkbox_label = Label(
            text="Auto Start/Stop after lap",
            color=TEXT,
            halign="left",
            valign="middle"
        )
        checkbox_label.bind(size=checkbox_label.setter('text_size'))
        checkbox_container.add_widget(auto_check)
        checkbox_container.add_widget(checkbox_label)
        
        add_btn = RButton(text="Add", color=ACCENT, size_hint_y=None, height=50)
        
        content = BoxLayout(orientation="vertical", spacing=12, padding=12)
        content.add_widget(Label(
            text="Name:",
            color=TEXT,
            size_hint_y=None,
            height=25,
            halign="left",
            valign="middle"
        ))
        content.add_widget(name_input)
        content.add_widget(Label(
            text="Description:",
            color=TEXT,
            size_hint_y=None,
            height=25
        ))
        content.add_widget(desc_input)
        content.add_widget(checkbox_container)
        content.add_widget(Label(
            text="Color:",
            color=TEXT,
            size_hint_y=None,
            height=25
        ))
        content.add_widget(color_picker)
        content.add_widget(add_btn)
        
        popup = Popup(title="New Label", content=content, size_hint=(0.95, 0.85))
        
        def add_label(*_):
            if name_input.text:
                selected_color = list(color_picker.color)
                self.lm.all().append({
                    "name": name_input.text,
                    "color": selected_color,
                    "desc": desc_input.text,
                    "is_default": False,
                    "auto_startstop": auto_check.active
                })
                self._update_labels()
                self.lm.save()
            popup.dismiss()
        
        add_btn.bind(on_press=add_label)
        popup.open()

    def _open_edit_label_popup(self, index: int) -> None:
        """Open popup for editing an existing label.
        
        Args:
            index: Index of label to edit
        """
        label = self.lm.groups[self.lm.group][index]
        
        # Cannot edit default label
        if label.get("is_default", False):
            dialog = create_info_dialog(
                title="Cannot Edit",
                message="The 'Default' label cannot be edited."
            )
            dialog.open()
            return
        
        name_input = TextInput(
            text=label["name"],
            size_hint_y=None,
            height=40
        )
        desc_input = TextInput(
            text=label.get("desc", ""),
            size_hint_y=None,
            height=40
        )
        
        color_picker = ColorPicker(color=label["color"])
        
        # Auto start/stop checkbox
        checkbox_container = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=12,
            padding=[0, 8]
        )
        auto_check = CheckBox(
            active=label.get("auto_startstop", False),
            size_hint_x=None,
            width=40
        )
        checkbox_label = Label(
            text="Auto Start/Stop after lap",
            color=TEXT,
            halign="left",
            valign="middle"
        )
        checkbox_label.bind(size=checkbox_label.setter('text_size'))
        checkbox_container.add_widget(auto_check)
        checkbox_container.add_widget(checkbox_label)
        
        save_btn = RButton(text="Save", color=ACCENT, size_hint_y=None, height=50)
        
        content = BoxLayout(orientation="vertical", spacing=12, padding=12)
        content.add_widget(Label(
            text="Name:",
            color=TEXT,
            size_hint_y=None,
            height=25
        ))
        content.add_widget(name_input)
        content.add_widget(Label(
            text="Description:",
            color=TEXT,
            size_hint_y=None,
            height=25
        ))
        content.add_widget(desc_input)
        content.add_widget(checkbox_container)
        content.add_widget(Label(
            text="Color:",
            color=TEXT,
            size_hint_y=None,
            height=25
        ))
        content.add_widget(color_picker)
        content.add_widget(save_btn)
        
        popup = Popup(title="Edit Label", content=content, size_hint=(0.95, 0.85))
        
        def save_label(*_):
            if name_input.text:
                label["name"] = name_input.text
                label["color"] = list(color_picker.color)
                label["desc"] = desc_input.text
                label["auto_startstop"] = auto_check.active
                self._update_labels()
                self.lm.save()
                
                # Notify timer screen to update affected laps
                if self.timer_screen:
                    self.timer_screen.refresh_laps_for_label(name_input.text)
                    self.timer_screen._save_to_storage()
            popup.dismiss()
        
        save_btn.bind(on_press=save_label)
        popup.open()

    # ==========================================================================
    # GROUP OPERATIONS
    # ==========================================================================

    def _change_group(self, instance, value: str) -> None:
        """Change the active label group.
        
        Args:
            instance: Spinner instance (unused)
            value: Selected group name
        """
        self.lm.group = value
        self.lm.idx = 0
        self.lm.save()
        self._update_labels()

    def _open_add_group_popup(self, *args) -> None:
        """Open popup for creating a new label group."""
        name_input = TextInput(
            hint_text="Group Name",
            size_hint_y=None,
            height=40
        )
        add_btn = RButton(text="Create", color=ACCENT, size_hint_y=None, height=50)
        
        content = BoxLayout(orientation="vertical", spacing=12, padding=12)
        content.add_widget(name_input)
        content.add_widget(add_btn)
        
        popup = Popup(
            title="New Label Group",
            content=content,
            size_hint=(0.8, 0.2)
        )
        
        def add_group(*_):
            if self.lm.add_group(name_input.text):
                self.group_spinner.values = list(self.lm.groups.keys())
                self.group_spinner.text = name_input.text
                self._change_group(None, name_input.text)
            popup.dismiss()
        
        add_btn.bind(on_press=add_group)
        popup.open()

    def _open_edit_group_popup(self, *args) -> None:
        """Open popup for editing/deleting current group."""
        current_group = self.lm.group
        
        # Cannot rename default group
        if current_group == "Default":
            dialog = create_info_dialog(
                title="Cannot Rename",
                message="The 'Default' group cannot be renamed."
            )
            dialog.open()
            return
        
        dialog = create_two_button_dialog(
            title="Edit Group",
            prompt="Edit group name:",
            input_text=current_group,
            left_button_text="Delete Group",
            right_button_text="Save",
            on_left=lambda: self._confirm_delete_group(current_group),
            on_right=lambda new_name: self._rename_group(current_group, new_name),
            left_danger=True
        )
        dialog.open()

    def _rename_group(self, old_name: str, new_name: str) -> None:
        """Rename a label group.
        
        Args:
            old_name: Current group name
            new_name: New group name
        """
        new_name = new_name.strip()
        if new_name and new_name != old_name:
            if self.lm.rename_group(old_name, new_name):
                self.group_spinner.values = list(self.lm.groups.keys())
                self.group_spinner.text = new_name
                self._change_group(None, new_name)

    def _confirm_delete_group(self, group_name: str) -> None:
        """Show confirmation dialog before deleting a group.
        
        Args:
            group_name: Name of group to delete
        """
        dialog = create_confirmation_dialog(
            title="Confirm Delete",
            message=f"Delete group '{group_name}'?\n\nAll labels in this group will be lost!",
            on_confirm=lambda: self._delete_group(group_name),
            danger=True
        )
        dialog.open()

    def _delete_group(self, group_name: str) -> None:
        """Delete a label group.
        
        Args:
            group_name: Name of group to delete
        """
        if self.lm.delete_group(group_name):
            self.group_spinner.values = list(self.lm.groups.keys())
            self.group_spinner.text = self.lm.group
            self._change_group(None, self.lm.group)

    # ==========================================================================
    # NAVIGATION
    # ==========================================================================

    def _navigate_back(self, *args) -> None:
        """Navigate back to timer screen."""
        self.manager.transition.direction = "right"
        self.manager.current = "timer"