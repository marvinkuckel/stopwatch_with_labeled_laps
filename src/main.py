"""Main application entry point for the Stopwatch app.

This module initializes and runs the Kivy application, setting up:
- Window configuration (size, aspect ratio)
- Screen manager with timer and labels screens
- Label manager for persistent data
- Font loading for icons
"""

from kivy.config import Config
from kivy.utils import platform

from constants import DESKTOP_RESOLUTION

# Configure window size for desktop platforms before other imports
if platform == "android":
    Config.set('graphics', 'multisamples', '0')
    Config.set('input', '%(name)s', 'probesysfs,provider=hidinput')
else:
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from managers import LabelManager
from screens import TimerScreen, LabelsScreen
from utils import download_font_awesome


# Additional configuration
Window.clearcolor = (0.12, 0.12, 0.12, 1)


class StopwatchApp(App):
    """Main application class for the Stopwatch.
    
    Manages the overall application lifecycle including:
    - Building the UI structure
    - Initializing managers
    - Handling app shutdown and state persistence
    
    Attributes:
        timer_screen: Reference to the main timer screen
    """
    
    def build(self) -> ScreenManager:
        """Build and configure the application structure.
        
        Returns:
            ScreenManager containing all application screens
        """
        # Load Font Awesome icons
        download_font_awesome()
        
        # Initialize label manager
        lm = LabelManager()
        
        # Create screen manager
        sm = ScreenManager()
        
        # Create screens
        self.timer_screen = TimerScreen(name="timer", lm=lm)
        labels_screen = LabelsScreen(name="labels", lm=lm)
        
        # Connect screens for cross-screen communication
        labels_screen.timer_screen = self.timer_screen
        
        # Add screens to manager
        sm.add_widget(self.timer_screen)
        sm.add_widget(labels_screen)
        
        return sm

    def on_stop(self) -> bool:
        """Handle application shutdown.
        
        Saves the current timer state before the app closes.
        
        Returns:
            True to allow the app to close
        """
        self.timer_screen._save_to_storage()
        return True


if __name__ == "__main__":
    StopwatchApp().run()