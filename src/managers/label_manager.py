"""Label and label group management with persistent storage.

This module provides the LabelManager class which handles:
- Managing multiple label groups
- Creating, editing, and deleting labels
- Persistent storage of labels to disk
- Label selection and iteration
"""

import json
import os
from typing import Dict, List, Optional


class LabelManager:
    """Manages label groups and their state with persistent storage.
    
    A label is a categorization marker for timer laps, containing:
    - name: Display name
    - color: RGBA color tuple
    - desc: Optional description
    - is_default: Whether this is the immutable default label
    - auto_startstop: Whether to automatically toggle start/stop on lap
    
    Labels are organized into groups, allowing different label sets
    for different activities or projects.
    
    Attributes:
        groups: Dictionary mapping group names to lists of labels
        group: Currently active group name
        idx: Index of currently selected label in active group
    """
    
    STORAGE_DIR = 'states'
    STORAGE_FILE = 'label_manager_data.json'
    
    def __init__(self):
        """Initialize the label manager and load saved state."""
        self.groups: Dict[str, List[dict]] = {}
        self.group: str = "Default"
        self.idx: int = 0
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """Load saved labels from persistent storage.
        
        Attempts to load label data from the JSON file. If the file
        doesn't exist or is corrupted, creates a default group instead.
        """
        try:
            file_path = os.path.join(self.STORAGE_DIR, self.STORAGE_FILE)
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.groups = data.get('groups', {})
                self.group = data.get('group', 'Default')
                self.idx = data.get('idx', 0)
                
                # Ensure we have at least one group
                if not self.groups:
                    self.add_group("Default")
        except (FileNotFoundError, json.JSONDecodeError):
            # No saved data - create default
            self.add_group("Default")

    def _save_to_storage(self) -> None:
        """Save current state to persistent storage.
        
        Creates the storage directory if it doesn't exist and writes
        the current label state to a JSON file.
        """
        try:
            os.makedirs(self.STORAGE_DIR, exist_ok=True)
            
            data = {
                'groups': self.groups,
                'group': self.group,
                'idx': self.idx
            }
            
            file_path = os.path.join(self.STORAGE_DIR, self.STORAGE_FILE)
            with open(file_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving labels: {e}")

    def current(self) -> dict:
        """Get the currently selected label.
        
        Returns:
            The label dictionary at the current index in the active group
        """
        return self.groups[self.group][self.idx]

    def all(self) -> List[dict]:
        """Get all labels in the current group.
        
        Returns:
            List of all label dictionaries in the active group
        """
        return self.groups[self.group]
    
    def add_group(self, group_name: str) -> bool:
        """Add a new label group.
        
        Creates a new group with a single default label. The default
        label cannot be deleted or edited.
        
        Args:
            group_name: Name for the new group
            
        Returns:
            True if group was created, False if name was empty or already exists
        """
        if group_name and group_name not in self.groups:
            self.groups[group_name] = [
                {
                    "name": "Default",
                    "color": [0.1, 0.1, 0.1, 1],
                    "is_default": True,
                    "auto_startstop": False
                }
            ]
            self._save_to_storage()
            return True
        return False
    
    def save(self) -> None:
        """Public method to trigger manual save.
        
        This is called from external code when changes are made
        that should be persisted immediately.
        """
        self._save_to_storage()
        
    def rename_group(self, old_name: str, new_name: str) -> bool:
        """Rename an existing label group.
        
        The "Default" group cannot be renamed. If the current group
        is being renamed, the active group name is updated accordingly.
        
        Args:
            old_name: Current name of the group
            new_name: New name for the group
            
        Returns:
            True if successful, False if new_name is empty, already exists,
            old_name doesn't exist, or trying to rename "Default"
        """
        if not new_name or new_name in self.groups or old_name not in self.groups:
            return False
        
        if old_name == "Default":
            return False  # Cannot rename default group
        
        # Move data to new key
        self.groups[new_name] = self.groups[old_name]
        del self.groups[old_name]
        
        # Update current group if necessary
        if self.group == old_name:
            self.group = new_name
        
        self._save_to_storage()
        return True

    def delete_group(self, group_name: str) -> bool:
        """Delete a label group.
        
        The "Default" group cannot be deleted. If the deleted group
        was active, switches to "Default" group.
        
        Args:
            group_name: Name of the group to delete
            
        Returns:
            True if successful, False if trying to delete "Default"
            or group doesn't exist
        """
        if group_name == "Default" or group_name not in self.groups:
            return False  # Cannot delete default group
        
        del self.groups[group_name]
        
        # Switch to Default if we deleted the active group
        if self.group == group_name:
            self.group = "Default"
            self.idx = 0
        
        self._save_to_storage()
        return True