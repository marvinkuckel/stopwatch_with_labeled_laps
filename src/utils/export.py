"""CSV export functionality for timer sessions.

This module handles exporting timer data to CSV format with
platform-specific file saving (Desktop, Android, iOS).
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Optional
from kivy.utils import platform

from .formatting import format_time


class CSVExporter:
    """Handles CSV export of timer sessions with platform-specific saving.
    
    Supports exporting lap data with labels, times, and metadata to CSV format.
    Handles different save mechanisms for Desktop, Android, and iOS platforms.
    """
    
    def __init__(self):
        """Initialize the CSV exporter."""
        self.exports_dir = 'exports'
        os.makedirs(self.exports_dir, exist_ok=True)
    
    def export_save_state(self, state_name: str, save_data: dict,
                         success_callback: Optional[callable] = None) -> bool:
        """Export a save state to CSV file.
        
        Creates a CSV file with:
        - Metadata header (name, creation time, total time, lap count)
        - Label information grouped by label groups
        - Lap data (number, time, label, type, notes)
        
        Args:
            state_name: Name of the save state
            save_data: Dictionary containing 'time', 'laps', and 'saved_at'
            success_callback: Optional callback(filepath) called on successful export
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            laps = save_data.get('laps', [])
            saved_at = save_data.get('saved_at', '')
            total_time = save_data.get('time', 0)
            
            # Generate filename with timestamp
            timestamp = self._format_timestamp(saved_at)
            csv_filename = f'{state_name}_{timestamp}.csv'
            
            # Build CSV content
            csv_content = self._build_csv_content(
                state_name, saved_at, total_time, laps
            )
            
            # Export using platform-specific method
            return self._export_platform_specific(
                csv_filename, csv_content, success_callback
            )
            
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return False
    
    def _build_csv_content(self, state_name: str, saved_at: str,
                          total_time: float, laps: List[dict]) -> List[List[str]]:
        """Build the complete CSV content structure.
        
        Args:
            state_name: Name of the save state
            saved_at: ISO format timestamp
            total_time: Total elapsed time in seconds
            laps: List of lap dictionaries
            
        Returns:
            List of rows (each row is a list of strings)
        """
        csv_content = []
        
        # Header with metadata
        csv_content.extend([
            ['# Save State Export'],
            ['# Name:', state_name],
            ['# Created:', saved_at],
            ['# Total Time:', format_time(total_time)],
            ['# Total Laps:', len(laps)],
            []  # Empty line
        ])
        
        # Label information grouped by groups
        csv_content.extend(self._build_label_info(laps))
        csv_content.append([])  # Empty line
        
        # Column headers
        csv_content.append(['Lap', 'Time', 'Label', 'SpecialType', 'Note'])
        
        # Lap data (oldest first)
        for i, lap in enumerate(reversed(laps)):
            lap_number = i + 1
            time_str = format_time(lap['t'])
            label_name = lap['lbl']['name']
            lap_type = lap.get('type', '')
            note = lap.get('note', '')
            
            csv_content.append([lap_number, time_str, label_name, lap_type, note])
        
        return csv_content
    
    def _build_label_info(self, laps: List[dict]) -> List[List[str]]:
        """Build label information section for CSV header.
        
        Groups labels by their label groups and lists unique labels
        with their descriptions and special types.
        
        Args:
            laps: List of lap dictionaries
            
        Returns:
            List of CSV rows containing label information
        """
        rows = [
            ['# Used Labels:'],
            ['#     Name', 'Description', 'SpecialType']
        ]
        
        # Collect unique labels by group
        labels_by_group = self._collect_labels_by_group(laps)
        
        # Add label info grouped by group
        for group_name, labels in sorted(labels_by_group.items()):
            rows.append([f'#   Group: {group_name}'])
            for label_name, label_info in sorted(labels.items()):
                auto_str = "Start/Stop" if label_info['auto_startstop'] else ""
                desc_str = label_info['desc'] if label_info['desc'] else ""
                rows.append([
                    '#     ' + str(label_name),
                    desc_str,
                    auto_str
                ])
        
        return rows
    
    def _collect_labels_by_group(self, laps: List[dict]) -> Dict[str, Dict]:
        """Collect unique labels organized by their groups.
        
        Args:
            laps: List of lap dictionaries
            
        Returns:
            Dictionary mapping group names to dictionaries of label data
        """
        labels_by_group = {}
        
        for lap in laps:
            label = lap['lbl']
            label_name = label['name']
            label_group = label.get('group', 'Default')
            
            if label_group not in labels_by_group:
                labels_by_group[label_group] = {}
            
            if label_name not in labels_by_group[label_group]:
                labels_by_group[label_group][label_name] = {
                    'color': label.get('color', [1, 1, 1, 0]),
                    'desc': label.get('desc', ''),
                    'auto_startstop': label.get('auto_startstop', False)
                }
        
        return labels_by_group
    
    def _format_timestamp(self, saved_at: str) -> str:
        """Format timestamp for filename.
        
        Args:
            saved_at: ISO format timestamp string
            
        Returns:
            Formatted timestamp string (YYYYMMDD_HHMMSS)
        """
        if saved_at:
            try:
                dt = datetime.fromisoformat(saved_at)
                return dt.strftime("%Y%m%d_%H%M%S")
            except:
                pass
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _export_platform_specific(self, filename: str, content: List[List[str]],
                                  success_callback: Optional[callable]) -> bool:
        """Export CSV using platform-appropriate method.
        
        Args:
            filename: Name for the CSV file
            content: List of CSV rows
            success_callback: Optional callback for success notification
            
        Returns:
            True if export was successful
        """
        if platform == 'android':
            return self._export_android(filename, content, success_callback)
        elif platform == 'ios':
            return self._export_ios(filename, content, success_callback)
        else:
            return self._export_desktop(filename, content, success_callback)
    
    def _export_desktop(self, filename: str, content: List[List[str]],
                       success_callback: Optional[callable]) -> bool:
        """Export CSV on desktop using native file dialog.
        
        Args:
            filename: Suggested filename
            content: CSV content rows
            success_callback: Success callback
            
        Returns:
            True if successful
        """
        try:
            # Try using tkinter for native dialog
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            # Open native save dialog
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename,
                title="Export Save State"
            )
            
            root.destroy()
            
            if filepath:  # User didn't cancel
                self._write_csv_file(filepath, content)
                
                if success_callback:
                    success_callback(filepath)
                
                print(f"✅ CSV exported successfully: {filepath}")
                return True
            else:
                print("Export cancelled")
                return False
                
        except ImportError:
            # Fallback if tkinter not available
            print("⚠️ tkinter not available, using fallback")
            return self._export_fallback(filename, content, success_callback)
        except Exception as e:
            print(f"❌ Desktop export error: {e}")
            return self._export_fallback(filename, content, success_callback)
    
    def _export_android(self, filename: str, content: List[List[str]],
                       success_callback: Optional[callable]) -> bool:
        """Export CSV on Android using share dialog.
        
        Args:
            filename: CSV filename
            content: CSV content rows
            success_callback: Success callback
            
        Returns:
            True if successful
        """
        try:
            from jnius import autoclass, cast
            
            # Android classes
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            Uri = autoclass('android.net.Uri')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            File = autoclass('java.io.File')
            
            # Save to cache directory
            context = PythonActivity.mActivity
            cache_dir = context.getCacheDir()
            file_path = File(cache_dir, filename)
            
            # Write CSV file
            self._write_csv_file(file_path.getAbsolutePath(), content)
            
            # Create content URI with FileProvider
            authority = String(context.getPackageName() + ".fileprovider")
            content_uri = FileProvider.getUriForFile(context, authority, file_path)
            
            # Create share intent
            share_intent = Intent()
            share_intent.setAction(Intent.ACTION_SEND)
            share_intent.setType(String("text/csv"))
            share_intent.putExtra(Intent.EXTRA_STREAM, 
                                cast('android.os.Parcelable', content_uri))
            share_intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            
            # Show share dialog
            chooser = Intent.createChooser(
                share_intent,
                cast('java.lang.CharSequence', String("Export CSV"))
            )
            context.startActivity(chooser)
            
            print("✅ Android share dialog opened")
            return True
            
        except Exception as e:
            print(f"❌ Android export error: {e}")
            # Fallback: Save to Downloads
            try:
                from android.storage import primary_external_storage_path
                downloads_path = os.path.join(
                    primary_external_storage_path(), 'Download'
                )
                os.makedirs(downloads_path, exist_ok=True)
                
                full_path = os.path.join(downloads_path, filename)
                self._write_csv_file(full_path, content)
                
                if success_callback:
                    success_callback(full_path)
                
                print(f"✅ CSV saved to Downloads: {full_path}")
                return True
            except Exception as e2:
                print(f"❌ Fallback failed: {e2}")
                return self._export_fallback(filename, content, success_callback)
    
    def _export_ios(self, filename: str, content: List[List[str]],
                   success_callback: Optional[callable]) -> bool:
        """Export CSV on iOS using share sheet.
        
        Args:
            filename: CSV filename
            content: CSV content rows
            success_callback: Success callback
            
        Returns:
            True if successful
        """
        try:
            from pyobjus import autoclass
            from pyobjus.dylib_manager import load_framework
            import tempfile
            
            load_framework('/System/Library/Frameworks/UIKit.framework')
            
            # Objective-C classes
            UIApplication = autoclass('UIApplication')
            NSURL = autoclass('NSURL')
            NSString = autoclass('NSString')
            UIActivityViewController = autoclass('UIActivityViewController')
            NSArray = autoclass('NSArray')
            
            # Save to temp directory
            temp_dir = tempfile.gettempdir()
            full_path = os.path.join(temp_dir, filename)
            self._write_csv_file(full_path, content)
            
            # Create file URL
            file_url = NSURL.fileURLWithPath_(
                NSString.alloc().initWithUTF8String_(full_path.encode('utf-8'))
            )
            
            # Create activity view controller
            items_array = NSArray.arrayWithObject_(file_url)
            activity_vc = UIActivityViewController.alloc() \
                .initWithActivityItems_applicationActivities_(items_array, None)
            
            # Show share sheet
            app = UIApplication.sharedApplication()
            root_vc = app.keyWindow().rootViewController()
            
            if root_vc:
                root_vc.presentViewController_animated_completion_(
                    activity_vc, True, None
                )
                print("✅ iOS share sheet opened")
                return True
            
        except Exception as e:
            print(f"❌ iOS export error: {e}")
            return self._export_fallback(filename, content, success_callback)
    
    def _export_fallback(self, filename: str, content: List[List[str]],
                        success_callback: Optional[callable]) -> bool:
        """Fallback export method - save to exports directory.
        
        Args:
            filename: CSV filename
            content: CSV content rows
            success_callback: Success callback
            
        Returns:
            True if successful
        """
        try:
            full_path = os.path.join(self.exports_dir, filename)
            self._write_csv_file(full_path, content)
            
            if success_callback:
                success_callback(full_path)
            
            print(f"✅ CSV exported (fallback): {full_path}")
            return True
            
        except Exception as e:
            print(f"❌ Fallback export error: {e}")
            return False
    
    def _write_csv_file(self, filepath: str, content: List[List[str]]) -> None:
        """Write CSV content to file.
        
        Args:
            filepath: Full path to CSV file
            content: List of rows to write
        """
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in content:
                writer.writerow(row)