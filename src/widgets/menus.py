"""Slide-in menu widgets for navigation and actions - RESPONSIVE VERSION.

This module provides menu widgets that slide in from screen edges,
commonly used for save state management and settings.
"""

from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation

from constants import (TEXT, MUTED, ACCENT, DANGER, PRIMARY, SURFACE_LIGHT,
                      ICON_TRASH, ICON_FONT, ICON_CLOCK, ICON_FLAG_CHECKERED, 
                      ICON_CALENDAR)
from widgets import RButton
from widgets.dialogs import create_text_input_dialog, create_confirmation_dialog
from utils import rh, rfs, rp, rs


class SlideMenu(ModalView):
    """Slide-in menu from left side for save state management.
    
    A modal overlay that slides in from the left, displaying a list
    of saved timer states with options to load, export, or delete them.
    
    Attributes:
        timer_screen: Reference to TimerScreen instance
        menu_container: Main container for menu content
        states_grid: Grid layout containing save state entries
    """
    
    def __init__(self, timer_screen, **kwargs):
        """Initialize the slide menu.
        
        Args:
            timer_screen: TimerScreen instance to interact with
            **kwargs: Additional keyword arguments passed to ModalView
        """
        # Configure ModalView properties
        kwargs['size_hint'] = (0.75, 1)
        kwargs['pos_hint'] = {'x': -0.75, 'y': 0}
        kwargs['background_color'] = (0, 0, 0, 0.5)
        kwargs['auto_dismiss'] = True
        super().__init__(**kwargs)
        
        self.timer_screen = timer_screen
        
        # Create menu container
        self.menu_container = BoxLayout(
            orientation='vertical',
            padding=0,
            spacing=0
        )
        
        # Draw menu background
        with self.menu_container.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.menu_container.bg = Rectangle()
        self.menu_container.bind(
            pos=lambda *_: setattr(self.menu_container.bg, 'pos', 
                                  self.menu_container.pos),
            size=lambda *_: setattr(self.menu_container.bg, 'size', 
                                   self.menu_container.size)
        )
        
        self._build_menu()
        self.add_widget(self.menu_container)
    
    def _build_menu(self) -> None:
        """Build the menu structure with header, content, and footer."""
        # Header
        header = BoxLayout(
            size_hint_y=None, 
            height=rh('header') + rp() * 2, 
            padding=rp() + 8
        )
        header_label = Label(
            text="Save States",
            font_size=rfs('title'),
            color=TEXT,
            halign="left",
            valign="middle"
        )
        header_label.bind(size=header_label.setter('text_size'))
        header.add_widget(header_label)
        
        # Scrollable content area
        scroll = ScrollView()
        self.states_grid = GridLayout(
            cols=1,
            spacing=rs(),
            size_hint_y=None,
            padding=[rp(), rp()]
        )
        self.states_grid.bind(minimum_height=self.states_grid.setter("height"))
        scroll.add_widget(self.states_grid)
        
        # Footer with action buttons
        footer = BoxLayout(
            size_hint_y=None,
            height=rh('footer') + rp(),
            padding=rp() + 8,
            spacing=rs() + 4,
            orientation='vertical'
        )
        
        new_save_btn = RButton(
            text="+ New Save State",
            color=ACCENT,
            size_hint_y=None,
            height=rh('button'),
            font_size=rfs('button')
        )
        new_save_btn.bind(on_press=self._create_new_save_state)
        footer.add_widget(new_save_btn)
        
        # Assemble menu
        self.menu_container.add_widget(header)
        self.menu_container.add_widget(scroll)
        self.menu_container.add_widget(footer)
        
        self._update_save_states_list()
    
    def _update_save_states_list(self) -> None:
        """Refresh the list of save states displayed in the menu."""
        self.states_grid.clear_widgets()
        
        save_states = self.timer_screen._get_all_save_states()
        
        if not save_states:
            # Show empty state message
            no_states_label = Label(
                text="No save states yet.\nCreate one to get started!",
                color=MUTED,
                font_size="14sp",
                halign="center"
            )
            no_states_label.bind(size=no_states_label.setter('text_size'))
            self.states_grid.add_widget(no_states_label)
        else:
            # Add a row for each save state
            for state_name in save_states:
                state_row = self._create_save_state_row(state_name)
                self.states_grid.add_widget(state_row)
    
    def _create_save_state_row(self, state_name: str):
        """Create a row displaying a save state with action buttons.
        
        Args:
            state_name: Name of the save state
            
        Returns:
            BoxLayout widget containing the save state display
        """
        # Calculate row height based on components
        row_height = rh('button') * 2 + rp() * 2 + rs()
        
        row = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=row_height,
            padding=rp(),
            spacing=rs() / 2
        )
        
        # Background
        with row.canvas.before:
            Color(0.14, 0.14, 0.14, 1)
            row.bg = Rectangle()
        row.bind(
            pos=lambda w, *_: setattr(w.bg, 'pos', w.pos),
            size=lambda w, *_: setattr(w.bg, 'size', w.size)
        )
        
        # Top row: Name and action buttons
        top_row = BoxLayout(size_hint_y=None, height=rh('button') - rs(), spacing=rs())
        
        name_label = Label(
            text=state_name,
            color=TEXT,
            font_size="16sp",
            bold=True,
            halign="left",
            valign="middle"
        )
        name_label.bind(size=name_label.setter('text_size'))
        
        # Button widths
        btn_width = rh('button') + rp()
        
        export_btn = RButton(
            text="Export",
            color=PRIMARY,
            size_hint_x=None,
            width=btn_width,
            font_size="13sp"
        )
        export_btn.bind(on_press=lambda *_: self._export_save_state(state_name))
        
        load_btn = RButton(
            text="Load",
            color=ACCENT,
            size_hint_x=None,
            width=btn_width,
            font_size="13sp"
        )
        load_btn.bind(on_press=lambda *_: self._load_save_state(state_name))
        
        delete_btn = RButton(
            text=ICON_TRASH,
            color=DANGER,
            size_hint_x=None,
            width=rh('button') - rs(),
            font_name=ICON_FONT,
            font_size="16sp"
        )
        delete_btn.bind(on_press=lambda *_: self._delete_save_state(state_name))
        
        top_row.add_widget(name_label)
        top_row.add_widget(export_btn)
        top_row.add_widget(load_btn)
        top_row.add_widget(delete_btn)
        
        # Bottom row: Metadata display
        bottom_row = self._create_metadata_row(state_name)
        
        row.add_widget(top_row)
        row.add_widget(bottom_row)
        
        return row
    
    def _create_metadata_row(self, state_name: str):
        """Create a row displaying save state metadata.
        
        Args:
            state_name: Name of the save state
            
        Returns:
            BoxLayout with time, lap count, and creation date
        """
        bottom_row = BoxLayout(
            size_hint_y=None,
            height=rh('button') - rp(),
            spacing=rs() + 4,
            padding=[0, rs() / 2]
        )
        
        metadata = self.timer_screen._get_save_state_metadata(state_name)
        
        if metadata:
            from utils import format_time
            
            # Timer time
            time_container = self._create_metadata_item(
                ICON_CLOCK,
                format_time(metadata['time']),
                0.3
            )
            
            # Lap count
            laps_container = self._create_metadata_item(
                ICON_FLAG_CHECKERED,
                f"{metadata['lap_count']} laps",
                0.25
            )
            
            # Creation date
            created_container = self._create_metadata_item(
                ICON_CALENDAR,
                metadata['created'],
                0.35
            )
            
            spacer = Widget(size_hint_x=0.1)
            
            bottom_row.add_widget(time_container)
            bottom_row.add_widget(laps_container)
            bottom_row.add_widget(spacer)
            bottom_row.add_widget(created_container)
        
        return bottom_row
    
    def _create_metadata_item(self, icon: str, text: str, 
                             size_hint: float):
        """Create a metadata display item with icon and text.
        
        Args:
            icon: Font Awesome unicode character
            text: Text to display
            size_hint: Horizontal size hint
            
        Returns:
            BoxLayout containing icon and text labels
        """
        container = BoxLayout(size_hint_x=size_hint, spacing=rs() / 2)
        
        icon_label = Label(
            text=icon,
            font_name=ICON_FONT,
            color=MUTED,
            font_size="12sp",
            size_hint_x=None,
            width=rp() * 1.5,
            halign="center",
            valign="middle"
        )
        icon_label.bind(size=icon_label.setter('text_size'))
        
        text_label = Label(
            text=text,
            color=MUTED,
            font_size="12sp",
            halign="left",
            valign="middle"
        )
        text_label.bind(size=text_label.setter('text_size'))
        
        container.add_widget(icon_label)
        container.add_widget(text_label)
        
        return container
    
    def _create_new_save_state(self, *args) -> None:
        """Open dialog for creating a new save state."""
        dialog = create_text_input_dialog(
            title="New Save State",
            prompt="Enter name for this save state:",
            hint_text="Save State Name",
            on_save=lambda name: self._save_with_name(name)
        )
        dialog.open()
    
    def _save_with_name(self, name: str) -> None:
        """Save current timer state with given name.
        
        Args:
            name: Name for the save state
        """
        if name.strip():
            self.timer_screen._save_state(name.strip())
            self._update_save_states_list()
    
    def _load_save_state(self, state_name: str) -> None:
        """Load a save state and close the menu.
        
        Args:
            state_name: Name of the save state to load
        """
        self.timer_screen._load_state(state_name)
        self.dismiss()
    
    def _delete_save_state(self, state_name: str) -> None:
        """Show confirmation dialog before deleting a save state.
        
        Args:
            state_name: Name of the save state to delete
        """
        dialog = create_confirmation_dialog(
            title="Confirm Delete",
            message=f"Delete '{state_name}'?",
            on_confirm=lambda: self._confirm_delete(state_name),
            danger=True
        )
        dialog.open()
    
    def _confirm_delete(self, state_name: str) -> None:
        """Delete a save state and refresh the list.
        
        Args:
            state_name: Name of the save state to delete
        """
        self.timer_screen._delete_save_state(state_name)
        self._update_save_states_list()
    
    def _export_save_state(self, state_name: str) -> None:
        """Export a save state to CSV.
        
        Args:
            state_name: Name of the save state to export
        """
        self.timer_screen._export_save_state_to_csv(state_name)
    
    def open(self, *args) -> None:
        """Open the menu with slide-in animation from left."""
        super().open(*args)
        self._update_save_states_list()
        
        # Animate slide-in
        anim = Animation(
            pos_hint={'x': 0, 'y': 0},
            duration=0.3,
            t='out_cubic'
        )
        anim.start(self)
    
    def dismiss(self, *args, **kwargs) -> None:
        """Close the menu with slide-out animation to left."""
        anim = Animation(
            pos_hint={'x': -0.75, 'y': 0},
            duration=0.3,
            t='out_cubic'
        )
        anim.bind(
            on_complete=lambda *_: super(SlideMenu, self).dismiss(*args, **kwargs)
        )
        anim.start(self)