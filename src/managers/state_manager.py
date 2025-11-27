"""Timer state persistence and save state management.

This module handles saving and loading timer states, including:
- Current timer state (time, laps, running status)
- Named save states for different sessions
- Save state metadata (creation time, lap count, etc.)
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class StateManager:
    """Manages timer state persistence and save states.
    
    Handles two types of state storage:
    1. Current state: Auto-saved timer state that persists across app restarts
    2. Named saves: User-created snapshots of timer state
    
    Attributes:
        STATES_DIR: Directory for current state storage
        SAVES_DIR: Directory for named save states
    """
    
    STATES_DIR = 'states'
    SAVES_DIR = 'saves'
    TIMER_STATE_FILE = 'timer_state.json'
    
    def __init__(self):
        """Initialize the state manager and create necessary directories."""
        os.makedirs(self.STATES_DIR, exist_ok=True)
        os.makedirs(self.SAVES_DIR, exist_ok=True)
    
    def save_current_state(self, time: float, laps: List[dict], 
                          label_startstop_state: Dict[str, bool]) -> bool:
        """Save the current timer state for auto-recovery.
        
        This is typically called automatically when the timer changes
        or when the app is closing.
        
        Args:
            time: Current timer value in seconds
            laps: List of lap dictionaries
            label_startstop_state: Dictionary tracking start/stop state per label
            
        Returns:
            True if save was successful, False on error
        """
        try:
            data = {
                'time': time,
                'laps': laps,
                'label_startstop_state': label_startstop_state
            }
            
            file_path = os.path.join(self.STATES_DIR, self.TIMER_STATE_FILE)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving timer state: {e}")
            return False
    
    def load_current_state(self) -> Optional[Dict]:
        """Load the saved timer state.
        
        Returns:
            Dictionary containing 'time', 'laps', and 'label_startstop_state',
            or None if no saved state exists or loading failed
        """
        try:
            file_path = os.path.join(self.STATES_DIR, self.TIMER_STATE_FILE)
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def create_save_state(self, name: str, time: float, laps: List[dict],
                         label_startstop_state: Dict[str, bool]) -> bool:
        """Create a named save state.
        
        If a save with this name already exists, appends a number
        in parentheses to make it unique (e.g., "Name(1)", "Name(2)").
        
        Args:
            name: Desired name for the save state
            time: Current timer value in seconds
            laps: List of lap dictionaries
            label_startstop_state: Dictionary tracking start/stop state per label
            
        Returns:
            True if save was successful, False on error
        """
        try:
            # Make name unique if needed
            unique_name = self._get_unique_save_name(name)
            
            data = {
                'time': time,
                'laps': laps,
                'label_startstop_state': label_startstop_state,
                'saved_at': datetime.now().isoformat()
            }
            
            file_path = os.path.join(self.SAVES_DIR, f'{unique_name}.json')
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Save state '{unique_name}' created!")
            return True
        except Exception as e:
            print(f"❌ Error creating save state: {e}")
            return False
    
    def load_save_state(self, name: str) -> Optional[Dict]:
        """Load a named save state.
        
        Args:
            name: Name of the save state to load
            
        Returns:
            Dictionary containing save state data, or None if not found
        """
        try:
            file_path = os.path.join(self.SAVES_DIR, f'{name}.json')
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"✅ Save state '{name}' loaded!")
            return data
        except Exception as e:
            print(f"❌ Error loading save state: {e}")
            return None
    
    def delete_save_state(self, name: str) -> bool:
        """Delete a named save state.
        
        Args:
            name: Name of the save state to delete
            
        Returns:
            True if deletion was successful, False if not found or error
        """
        try:
            file_path = os.path.join(self.SAVES_DIR, f'{name}.json')
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"✅ Save state '{name}' deleted!")
                return True
        except Exception as e:
            print(f"❌ Error deleting save state: {e}")
        return False
    
    def list_save_states(self) -> List[str]:
        """Get a list of all save state names.
        
        Returns:
            List of save state names, sorted newest first
        """
        try:
            if not os.path.exists(self.SAVES_DIR):
                return []
            
            files = [f[:-5] for f in os.listdir(self.SAVES_DIR) 
                    if f.endswith('.json')]
            return sorted(files, reverse=True)
        except Exception as e:
            print(f"❌ Error listing save states: {e}")
            return []
    
    def get_save_metadata(self, name: str) -> Optional[Dict]:
        """Get metadata for a save state without loading full data.
        
        Args:
            name: Name of the save state
            
        Returns:
            Dictionary with 'created' (formatted string), 'time' (seconds),
            and 'lap_count', or None if not found
        """
        try:
            file_path = os.path.join(self.SAVES_DIR, f'{name}.json')
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Format creation date
            saved_at = data.get('saved_at', '')
            if saved_at:
                try:
                    dt = datetime.fromisoformat(saved_at)
                    created_str = dt.strftime("%d.%m.%y %H:%M")
                except:
                    created_str = "Unknown"
            else:
                created_str = "Unknown"
            
            return {
                'created': created_str,
                'time': data.get('time', 0),
                'lap_count': len(data.get('laps', []))
            }
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
            return None
    
    def _get_unique_save_name(self, base_name: str) -> str:
        """Generate a unique save name by appending numbers if needed.
        
        Args:
            base_name: Desired save name
            
        Returns:
            Unique name (either base_name or base_name(N))
        """
        existing_states = self.list_save_states()
        
        if base_name not in existing_states:
            return base_name
        
        # Append number in parentheses
        counter = 1
        while f"{base_name}({counter})" in existing_states:
            counter += 1
        
        return f"{base_name}({counter})"