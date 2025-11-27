"""Main timer screen with stopwatch and lap functionality.

This module contains the primary timer interface where users can:
- Start/stop the timer
- Record laps with labels
- Add notes to laps
- Save and load timer states
- Export sessions to CSV
"""

from typing import Dict, List, Optional
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock

from constants import (ACCENT, DANGER, ICON_BARS, ICON_FONT, ICON_PEN,
                      ICON_PLAY, ICON_STOP, ICON_TAGS, MUTED, SURFACE_LIGHT, TEXT)
from widgets import RButton, LabelSpinner, SlideMenu
from utils import format_time, CSVExporter
from managers import StateManager


class TimerScreen(Screen):
    """Main timer screen with stopwatch and lap recording.
    
    This screen provides the primary stopwatch interface with features:
    - Start/stop timer with millisecond precision
    - Lap recording with customizable labels
    - Automatic start/stop tracking for labels
    - Notes for individual laps
    - Persistent state across app restarts
    - Named save states for different sessions
    
    Attributes:
        lm: LabelManager instance for label data
        state_manager: StateManager for persistence
        time: Current elapsed time in seconds
        running: Whether timer is currently running
        laps: List of recorded lap dictionaries
        provisional_label: Label selected for next lap (if any)
        label_startstop_state: Dict tracking start/stop state per label
    """
    
    def __init__(self, lm, **kwargs):
        """Initialize the timer screen.
        
        Args:
            lm: LabelManager instance
            **kwargs: Additional keyword arguments passed to Screen
        """
        super().__init__(**kwargs)
        
        self.lm = lm
        self.state_manager = StateManager()
        self.csv_exporter = CSVExporter()
        
        # Timer state
        self.time: float = 0
        self.running: bool = False
        self.laps: List[dict] = []
        self.provisional_label: Optional[dict] = None
        self.label_startstop_state: Dict[str, bool] = {}
        
        self._build_ui()
        self._load_from_storage()

    # ==========================================================================
    # UI CONSTRUCTION
    # ==========================================================================

    def _build_ui(self) -> None:
        """Build the complete user interface."""
        root = BoxLayout(orientation="vertical")
        
        root.add_widget(self._create_header())
        root.add_widget(self._create_time_display())
        root.add_widget(self._create_provisional_label_selector())
        root.add_widget(self._create_lap_list())
        root.add_widget(self._create_footer())
        
        self.add_widget(root)

    def _create_header(self) -> BoxLayout:
        """Create header with menu button, title, and labels button.
        
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
        
        # Burger menu button
        burger_btn = RButton(
            text=ICON_BARS,
            color=SURFACE_LIGHT,
            size_hint_x=None,
            font_name=ICON_FONT,
            font_size="22sp"
        )
        burger_btn.bind(on_press=self._open_save_menu)
        burger_btn.size[0] = 50
        
        # Title
        title = Label(
            text="Timer",
            halign="left",
            valign="middle",
            padding=[8, 0, 0, 0],
            color=TEXT,
            font_size="25sp"
        )
        title.bind(size=title.setter('text_size'))
        
        # Labels/tags button
        labels_btn = RButton(
            text=ICON_TAGS,
            color=SURFACE_LIGHT,
            size_hint_x=None,
            font_name=ICON_FONT,
            font_size="22sp"
        )
        labels_btn.bind(on_press=self._navigate_to_labels)
        labels_btn.size[0] = 50
        
        header.add_widget(burger_btn)
        header.add_widget(title)
        header.add_widget(labels_btn)
        
        return header

    def _create_time_display(self) -> BoxLayout:
        """Create the large time display.
        
        Returns:
            BoxLayout containing time label
        """
        self.time_label = Label(
            text="0:00.000",
            font_size="56sp",
            color=TEXT
        )
        
        time_box = BoxLayout(size_hint_y=None, height=100, padding=12)
        time_box.add_widget(self.time_label)
        
        return time_box

    def _create_provisional_label_selector(self) -> BoxLayout:
        """Create the 'Next Label' selector for upcoming laps.
        
        Returns:
            BoxLayout containing label text and spinner
        """
        outer_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=80,
            padding=[8, 8]
        )
        
        # Background
        with outer_container.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            outer_container.bg = Rectangle()
        outer_container.bind(
            pos=lambda *_: setattr(outer_container.bg, 'pos', 
                                  outer_container.pos),
            size=lambda *_: setattr(outer_container.bg, 'size', 
                                   outer_container.size)
        )
        
        # Label
        label_text = Label(
            text="Next Label:",
            color=MUTED,
            size_hint_y=None,
            height=20,
            halign="left",
            valign="bottom",
            font_size="13sp"
        )
        label_text.bind(size=label_text.setter('text_size'))
        
        # Create temporary lap dict for spinner
        temp_label = self.lm.current().copy()
        temp_label['group'] = self.lm.group
        temp_lap = {"lbl": temp_label}
        
        self.provisional_spinner = LabelSpinner(
            lap=temp_lap,
            label_manager=self.lm,
            on_change=self._on_provisional_label_change,
            size_hint_y=None,
            height=40
        )
        
        outer_container.add_widget(label_text)
        outer_container.add_widget(self.provisional_spinner)
        
        return outer_container

    def _create_lap_list(self) -> ScrollView:
        """Create scrollable list of laps.
        
        Returns:
            ScrollView containing lap grid
        """
        scroll = ScrollView()
        
        self.lap_grid = GridLayout(cols=1, spacing=0, size_hint_y=None)
        self.lap_grid.bind(minimum_height=self.lap_grid.setter("height"))
        
        scroll.add_widget(self.lap_grid)
        
        return scroll

    def _create_footer(self) -> BoxLayout:
        """Create footer with start/stop and lap/reset buttons.
        
        Returns:
            BoxLayout containing control buttons
        """
        self.left_btn = RButton(text="Start", color=ACCENT, font_size="20sp")
        self.left_btn.bind(on_press=self._toggle_timer)
        
        self.right_btn = RButton(text="Reset", color=SURFACE_LIGHT, 
                                font_size="20sp")
        self.right_btn.bind(on_press=self._lap_or_reset)
        
        footer = BoxLayout(size_hint_y=None, height=110, padding=20, spacing=20)
        footer.add_widget(self.left_btn)
        footer.add_widget(self.right_btn)
        
        return footer

    # ==========================================================================
    # TIMER CONTROL
    # ==========================================================================

    def _toggle_timer(self, *args) -> None:
        """Toggle timer between running and stopped states."""
        self.running = not self.running
        
        if self.running:
            Clock.schedule_interval(self._tick, 0.01)
        else:
            Clock.unschedule(self._tick)
        
        self._update_buttons()

    def _tick(self, dt: float) -> None:
        """Update timer display.
        
        Args:
            dt: Delta time since last tick
        """
        self.time += dt
        self.time_label.text = format_time(self.time)

    def _lap_or_reset(self, *args) -> None:
        """Create lap if running, reset if stopped."""
        if self.running:
            self._add_lap()
        else:
            self._reset()

    def _reset(self) -> None:
        """Reset timer to initial state."""
        self.time = 0
        self.time_label.text = format_time(0)
        self.laps.clear()
        self.lap_grid.clear_widgets()
        self.label_startstop_state.clear()
        self._save_to_storage()

    def _update_buttons(self) -> None:
        """Update button appearance based on timer state."""
        if self.running:
            self.left_btn.text = "Stop"
            self.left_btn.set_color(DANGER)
            self.right_btn.text = "Lap"
        else:
            self.left_btn.text = "Start"
            self.left_btn.set_color(ACCENT)
            self.right_btn.text = "Reset"

    # ==========================================================================
    # LAP MANAGEMENT
    # ==========================================================================

    def _add_lap(self, *args) -> None:
        """Record a new lap with current time and label."""
        # Determine which label to use
        if self.provisional_label:
            label = self.provisional_label
            label_copy = label.copy()
            
            # Find group for this label
            label_group = self._find_label_group(label)
            label_copy['group'] = label_group
        else:
            # Use current label
            label = self.lm.current()
            label_copy = label.copy()
            label_copy['group'] = self.lm.group
        
        # Determine lap type for auto-start/stop labels
        lap_type = None
        if label.get("auto_startstop", False):
            label_name = label["name"]
            is_start = not self.label_startstop_state.get(label_name, False)
            self.label_startstop_state[label_name] = is_start
            lap_type = "Start" if is_start else "Stop"
        
        # Create lap entry
        lap_data = {
            "t": self.time,
            "lbl": label_copy,
            "type": lap_type
        }
        self.laps.insert(0, lap_data)
        
        self._refresh_all_lap_rows()
        self._save_to_storage()
        
        # Reset provisional selection
        self.provisional_label = None
        self._update_provisional_display()

    def _find_label_group(self, label: dict) -> str:
        """Find which group a label belongs to.
        
        Args:
            label: Label dictionary to search for
            
        Returns:
            Group name, defaults to "Default" if not found
        """
        for group_name, labels in self.lm.groups.items():
            for lbl in labels:
                if (lbl["name"] == label["name"] and
                    lbl.get("color") == label.get("color") and
                    lbl.get("is_default") == label.get("is_default")):
                    return group_name
        return "Default"

    def _create_lap_row(self, number: int, lap: dict) -> BoxLayout:
        """Create a visual row for displaying a lap.
        
        Args:
            number: Lap number (1 = oldest)
            lap: Lap data dictionary
            
        Returns:
            BoxLayout containing lap information
        """
        row = BoxLayout(size_hint_y=None, height=64, padding=12, spacing=10)
        
        # Background
        with row.canvas.before:
            Color(0.14, 0.14, 0.14, 1)
            row.bg = Rectangle()
        row.bind(
            pos=lambda i, *_: setattr(i.bg, 'pos', i.pos),
            size=lambda i, *_: setattr(i.bg, 'size', i.size)
        )
        
        # Lap number
        num_label = Label(
            text=f"{number}.",
            size_hint_x=0.05,
            color=TEXT,
            font_size="16sp",
            halign="left",
            valign="center"
        )
        num_label.bind(size=num_label.setter('text_size'))

        # Start/Stop indicator
        lap_type = lap.get("type")
        if lap_type:
            indicator = Label(
                text=ICON_PLAY if lap_type == "Start" else ICON_STOP,
                font_name=ICON_FONT,
                font_size="14sp",
                color=ACCENT if lap_type == "Start" else DANGER,
                size_hint_x=None,
                width=28,
                halign="center",
                valign="middle"
            )
            indicator.bind(size=indicator.setter('text_size'))
        else:
            indicator = Widget(size_hint_x=None, width=28)
        
        # Time
        time_label = Label(
            text=format_time(lap["t"]),
            size_hint_x=0.1,
            color=TEXT,
            font_size="16sp",
            halign="center"
        )
        
        # Label selector
        label_spinner = LabelSpinner(
            lap=lap,
            label_manager=self.lm,
            on_change=lambda lbl: self._on_lap_label_changed(lap),
            size_hint_x=0.6
        )
        
        # Note button
        pencil_btn = RButton(
            text=ICON_PEN,
            color=SURFACE_LIGHT,
            size_hint_x=0.08,
            font_name=ICON_FONT,
            font_size="18sp"
        )
        pencil_btn.bind(on_press=lambda *_, l=lap: self._open_note_popup(l, 
                                                                         pencil_btn))
        
        row.add_widget(num_label)
        row.add_widget(indicator)
        row.add_widget(time_label)
        row.add_widget(label_spinner)
        row.add_widget(pencil_btn)
        
        return row

    def _refresh_all_lap_rows(self) -> None:
        """Rebuild all lap rows from scratch."""
        self.lap_grid.clear_widgets()
        
        for i, lap in enumerate(self.laps):
            lap_number = len(self.laps) - i
            lap_widget = self._create_lap_row(lap_number, lap)
            self.lap_grid.add_widget(lap_widget, index=0)

    def _on_lap_label_changed(self, lap: dict) -> None:
        """Handle label change for a lap.
        
        Args:
            lap: The lap whose label was changed
        """
        # Remove type if new label doesn't have auto_startstop
        if not lap["lbl"].get("auto_startstop", False):
            lap["type"] = None
        else:
            # Set type based on current state if not set
            if lap.get("type") is None:
                label_name = lap["lbl"]["name"]
                is_start = not self.label_startstop_state.get(label_name, False)
                self.label_startstop_state[label_name] = is_start
                lap["type"] = "Start" if is_start else "Stop"
        
        # Recalculate all start/stop states
        self._recalculate_startstop_states()
        self._refresh_all_lap_rows()
        self._save_to_storage()

    def _recalculate_startstop_states(self) -> None:
        """Recalculate start/stop states in chronological order.
        
        Processes laps from oldest to newest to maintain correct
        start/stop alternation for auto-start/stop labels.
        """
        temp_states = {}
        
        # Process laps in chronological order (reverse list)
        for i in range(len(self.laps) - 1, -1, -1):
            lap = self.laps[i]
            
            if lap["lbl"].get("auto_startstop", False):
                label_name = lap["lbl"]["name"]
                
                # Toggle state
                is_start = not temp_states.get(label_name, False)
                temp_states[label_name] = is_start
                lap["type"] = "Start" if is_start else "Stop"
            else:
                lap["type"] = None
        
        self.label_startstop_state = temp_states.copy()

    def refresh_laps_for_label(self, label_name: str) -> None:
        """Update all laps using a specific label.
        
        Called when a label is edited in the settings screen.
        
        Args:
            label_name: Name of the label that was modified
        """
        # Update laps with this label
        for lap in self.laps:
            if lap["lbl"]["name"] == label_name:
                # Find updated label
                updated_label = None
                for lbl in self.lm.all():
                    if lbl["name"] == label_name:
                        updated_label = lbl
                        break
                
                if updated_label:
                    lap["lbl"] = updated_label.copy()
        
        # Recalculate states and refresh display
        self._recalculate_startstop_states()
        self._refresh_all_lap_rows()

    # ==========================================================================
    # PROVISIONAL LABEL
    # ==========================================================================

    def _on_provisional_label_change(self, label_data: dict) -> None:
        """Handle provisional label selection change.
        
        Args:
            label_data: Selected label dictionary
        """
        label_with_group = label_data.copy()
        label_with_group['group'] = self.lm.group
        self.provisional_label = label_with_group
        
        # Update label manager index
        for i, lbl in enumerate(self.lm.all()):
            if lbl["name"] == label_data["name"]:
                self.lm.idx = i
                break

    def _update_provisional_display(self) -> None:
        """Update the provisional label spinner display."""
        if hasattr(self, 'provisional_spinner'):
            self.provisional_spinner.lap["lbl"] = self.lm.current().copy()
            self.provisional_spinner._update_display()

    # ==========================================================================
    # NOTES
    # ==========================================================================

    def _open_note_popup(self, lap: dict, pencil_btn: RButton) -> None:
        """Open popup for editing lap note.
        
        Args:
            lap: Lap dictionary to edit note for
            pencil_btn: Button to update color when note is added
        """
        text_input = TextInput(
            text=lap.get("note", ""),
            multiline=True,
            font_size=24
        )
        
        save_btn = RButton(text="Save", color=ACCENT, size_hint_y=None, height=40)
        
        content = BoxLayout(orientation="vertical", spacing=8, padding=8)
        content.add_widget(text_input)
        content.add_widget(save_btn)
        
        popup = Popup(title="Note", content=content, size_hint=(0.9, 0.7))
        
        def save_note(*args):
            lap["note"] = text_input.text
            self._save_to_storage()
            popup.dismiss()
            # Update button color based on note presence
            pencil_btn.set_color(ACCENT if text_input.text else SURFACE_LIGHT)
        
        save_btn.bind(on_press=save_note)
        popup.open()

    # ==========================================================================
    # NAVIGATION
    # ==========================================================================

    def _navigate_to_labels(self, *args) -> None:
        """Navigate to labels management screen."""
        self.manager.transition.direction = "left"
        self.manager.current = "labels"

    def _open_save_menu(self, *args) -> None:
        """Open the slide-in save state menu."""
        menu = SlideMenu(timer_screen=self)
        menu.open()

    # ==========================================================================
    # STATE PERSISTENCE
    # ==========================================================================

    def _save_to_storage(self) -> None:
        """Save current timer state to persistent storage."""
        self.state_manager.save_current_state(
            self.time,
            self.laps,
            self.label_startstop_state
        )

    def _load_from_storage(self) -> None:
        """Load saved timer state from storage."""
        state = self.state_manager.load_current_state()
        
        if state:
            self.time = state.get('time', 0)
            self.laps = state.get('laps', [])
            self.label_startstop_state = state.get('label_startstop_state', {})
            
            # Sync labels with current label manager
            self._sync_labels_with_manager()
            
            # Update UI
            self.time_label.text = format_time(self.time)
            self._refresh_all_lap_rows()

    def _sync_labels_with_manager(self) -> None:
        """Sync lap labels with current label manager state.
        
        Ensures that labels in saved laps match current label definitions,
        updating colors, descriptions, and other properties.
        """
        for lap in self.laps:
            label_name = lap['lbl']['name']
            label_group = lap['lbl'].get('group', 'Default')
            
            # Try to find label in its group
            found = False
            if label_group in self.lm.groups:
                for lbl in self.lm.groups[label_group]:
                    if lbl['name'] == label_name:
                        updated_label = lbl.copy()
                        updated_label['group'] = label_group
                        lap['lbl'] = updated_label
                        found = True
                        break
            
            # If not found, search all groups
            if not found:
                for group_name, labels in self.lm.groups.items():
                    for lbl in labels:
                        if lbl['name'] == label_name:
                            updated_label = lbl.copy()
                            updated_label['group'] = group_name
                            lap['lbl'] = updated_label
                            found = True
                            break
                    if found:
                        break

    # ==========================================================================
    # SAVE STATES (delegated to StateManager, kept for compatibility)
    # ==========================================================================

    def _save_state(self, state_name: Optional[str] = None) -> bool:
        """Save current timer state with a name.
        
        Args:
            state_name: Name for the save state, or None for timestamp
            
        Returns:
            True if successful
        """
        if state_name is None:
            from datetime import datetime
            state_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        return self.state_manager.create_save_state(
            state_name,
            self.time,
            self.laps,
            self.label_startstop_state
        )

    def _load_state(self, state_name: str) -> bool:
        """Load a named save state.
        
        Args:
            state_name: Name of the save state
            
        Returns:
            True if successful
        """
        state = self.state_manager.load_save_state(state_name)
        
        if state:
            self.time = state.get('time', 0)
            self.laps = state.get('laps', [])
            self.label_startstop_state = state.get('label_startstop_state', {})
            
            # Update UI
            self.time_label.text = format_time(self.time)
            self._refresh_all_lap_rows()
            
            # Save to current state
            self._save_to_storage()
            return True
        
        return False

    def _get_all_save_states(self) -> List[str]:
        """Get list of all save states.
        
        Returns:
            List of save state names
        """
        return self.state_manager.list_save_states()

    def _delete_save_state(self, state_name: str) -> bool:
        """Delete a save state.
        
        Args:
            state_name: Name of save state to delete
            
        Returns:
            True if successful
        """
        return self.state_manager.delete_save_state(state_name)

    def _get_save_state_metadata(self, state_name: str) -> Optional[Dict]:
        """Get metadata for a save state.
        
        Args:
            state_name: Name of the save state
            
        Returns:
            Dictionary with metadata, or None if not found
        """
        return self.state_manager.get_save_metadata(state_name)

    # ==========================================================================
    # CSV EXPORT
    # ==========================================================================

    def _export_save_state_to_csv(self, state_name: str) -> bool:
        """Export a save state to CSV file.
        
        Args:
            state_name: Name of the save state to export
            
        Returns:
            True if successful
        """
        # Load the save state data
        state = self.state_manager.load_save_state(state_name)
        
        if not state:
            return False
        
        # Export using CSV exporter
        return self.csv_exporter.export_save_state(
            state_name,
            state,
            success_callback=self._show_export_success
        )

    def _show_export_success(self, filepath: str) -> None:
        """Show success message after CSV export.
        
        Args:
            filepath: Path where CSV was saved
        """
        from widgets import create_info_dialog
        
        dialog = create_info_dialog(
            title="Export Successful",
            message=f"Export successful!\n\nSaved to:\n{filepath}"
        )
        dialog.open()