"""Manager classes for data and state persistence.

This package contains manager classes that handle:
- Label groups and label data (LabelManager)
- Timer state and save states (StateManager)
"""

from .label_manager import LabelManager
from .state_manager import StateManager

__all__ = [
    'LabelManager',
    'StateManager',
]