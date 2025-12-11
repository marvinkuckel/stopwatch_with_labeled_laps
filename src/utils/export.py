"""CSV export - FIXED: Wait for permissions before showing dialog."""

import os
import csv
from datetime import datetime
from typing import List, Dict, Optional
from kivy.utils import platform
from kivy.clock import Clock

from .formatting import format_time


class CSVExporter:
    """Handles CSV export with proper permission waiting."""
    
    def __init__(self):
        """Initialize the CSV exporter."""
        self.exports_dir = 'exports'
        if platform not in ('android', 'ios'):
            os.makedirs(self.exports_dir, exist_ok=True)
        
        self.last_error = None
    
    def export_save_state(self, state_name: str, save_data: dict,
                         success_callback: Optional[callable] = None,
                         error_callback: Optional[callable] = None) -> bool:
        """Export a save state to CSV file."""
        print(f"\n{'='*60}")
        print(f"🚀 EXPORT STARTED: {state_name}")
        print(f"{'='*60}")
        
        try:
            laps = save_data.get('laps', [])
            saved_at = save_data.get('saved_at', '')
            total_time = save_data.get('time', 0)
            
            print(f"📊 Data: {len(laps)} laps, {total_time:.2f}s total")
            
            # Generate filename with timestamp
            timestamp = self._format_timestamp(saved_at)
            csv_filename = f'{state_name}_{timestamp}.csv'
            
            print(f"📝 Filename: {csv_filename}")
            
            # Build CSV content
            print(f"🔨 Building CSV content...")
            csv_content = self._build_csv_content(
                state_name, saved_at, total_time, laps
            )
            print(f"✅ CSV content built: {len(csv_content)} rows")
            
            # Export using platform-specific method
            print(f"📱 Platform: {platform}")
            result = self._export_platform_specific(
                csv_filename, csv_content, success_callback, error_callback
            )
            
            print(f"{'='*60}")
            print(f"{'✅ SUCCESS' if result else '❌ FAILED'}")
            print(f"{'='*60}\n")
            
            return result
            
        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            print(f"❌ EXCEPTION: {error_msg}")
            import traceback
            traceback.print_exc()
            
            self.last_error = error_msg
            
            if error_callback:
                error_callback(error_msg)
            
            return False
    
    def _build_csv_content(self, state_name: str, saved_at: str,
                          total_time: float, laps: List[dict]) -> List[List[str]]:
        """Build the complete CSV content structure."""
        csv_content = []
        
        # Header with metadata
        csv_content.extend([
            ['# Save State Export'],
            ['# Name:', state_name],
            ['# Created:', saved_at],
            ['# Total Time:', format_time(total_time)],
            ['# Total Laps:', len(laps)],
            []
        ])
        
        # Label information
        csv_content.extend(self._build_label_info(laps))
        csv_content.append([])
        
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
        """Build label information section for CSV header."""
        rows = [
            ['# Used Labels:'],
            ['#     Name', 'Description', 'SpecialType']
        ]
        
        labels_by_group = self._collect_labels_by_group(laps)
        
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
        """Collect unique labels organized by their groups."""
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
        """Format timestamp for filename."""
        if saved_at:
            try:
                dt = datetime.fromisoformat(saved_at)
                return dt.strftime("%Y%m%d_%H%M%S")
            except:
                pass
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _export_platform_specific(self, filename: str, content: List[List[str]],
                                  success_callback: Optional[callable],
                                  error_callback: Optional[callable]) -> bool:
        """Export CSV using platform-appropriate method."""
        if platform == 'android':
            return self._export_android(filename, content, success_callback, error_callback)
        elif platform == 'ios':
            return self._export_ios(filename, content, success_callback, error_callback)
        else:
            return self._export_desktop(filename, content, success_callback, error_callback)
    
    def _export_desktop(self, filename: str, content: List[List[str]],
                       success_callback: Optional[callable],
                       error_callback: Optional[callable]) -> bool:
        """Export CSV on desktop using native file dialog."""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename,
                title="Export Save State"
            )
            
            root.destroy()
            
            if filepath:
                self._write_csv_file(filepath, content)
                
                if success_callback:
                    success_callback(filepath)
                
                print(f"✅ CSV exported: {filepath}")
                return True
            else:
                print("Export cancelled")
                return False
                
        except ImportError:
            print("⚠️ tkinter not available, using fallback")
            return self._export_fallback(filename, content, success_callback, error_callback)
        except Exception as e:
            print(f"❌ Desktop export error: {e}")
            if error_callback:
                error_callback(str(e))
            return False
    
    def _export_android(self, filename: str, content: List[List[str]],
                       success_callback: Optional[callable],
                       error_callback: Optional[callable]) -> bool:
        """Export CSV on Android - REQUEST PERMISSIONS FIRST, THEN WAIT."""
        print(f"🤖 ANDROID EXPORT START")
        
        try:
            from android.permissions import request_permissions, Permission, check_permission
            
            print(f"📦 Requesting permissions...")
            
            # Request permissions
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])
            
            # IMPORTANT: Schedule the actual export to happen AFTER permissions are granted
            # Use Clock.schedule_once to delay execution
            def do_export_after_permission(dt):
                self._do_android_export_with_permission(
                    filename, content, success_callback, error_callback
                )
            
            # Wait 2 seconds for user to grant permission
            print(f"⏳ Waiting for permission grant (2 seconds)...")
            Clock.schedule_once(do_export_after_permission, 2.0)
            
            # Return True immediately - actual result will be in callback
            return True
            
        except Exception as e:
            error_msg = f"Android export failed: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            
            if error_callback:
                error_callback(error_msg)
            
            return False
    
    def _do_android_export_with_permission(self, filename: str, content: List[List[str]],
                                          success_callback: Optional[callable],
                                          error_callback: Optional[callable]) -> bool:
        """Actually do the Android export AFTER permissions are granted."""
        print(f"🤖 ANDROID EXPORT - After permission wait")
        
        try:
            from jnius import autoclass
            from android.permissions import check_permission, Permission
            
            # Check if we actually got permission
            has_write = check_permission(Permission.WRITE_EXTERNAL_STORAGE)
            has_read = check_permission(Permission.READ_EXTERNAL_STORAGE)
            
            print(f"📋 Permissions: WRITE={has_write}, READ={has_read}")
            
            print(f"📦 Importing Android modules...")
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Environment = autoclass('android.os.Environment')
            File = autoclass('java.io.File')
            
            context = PythonActivity.mActivity
            
            # Try multiple paths in order of preference
            paths_to_try = []
            
            # 1. App-specific external directory (no permissions needed Android 10+)
            try:
                app_external_dir = context.getExternalFilesDir(None)
                paths_to_try.append(('App Files', app_external_dir))
                print(f"✅ Found App External: {app_external_dir.getAbsolutePath()}")
            except Exception as e:
                print(f"⚠️ Could not access App External: {e}")
            
            # 2. Downloads directory (if we have permission)
            if has_write:
                try:
                    downloads_dir = Environment.getExternalStoragePublicDirectory(
                        Environment.DIRECTORY_DOWNLOADS
                    )
                    paths_to_try.insert(0, ('Downloads', downloads_dir))
                    print(f"✅ Found Downloads: {downloads_dir.getAbsolutePath()}")
                except Exception as e:
                    print(f"⚠️ Could not access Downloads: {e}")
            
            # 3. Documents directory (if we have permission)
            if has_write:
                try:
                    docs_dir = Environment.getExternalStoragePublicDirectory(
                        Environment.DIRECTORY_DOCUMENTS
                    )
                    paths_to_try.append(('Documents', docs_dir))
                    print(f"✅ Found Documents: {docs_dir.getAbsolutePath()}")
                except Exception as e:
                    print(f"⚠️ Could not access Documents: {e}")
            
            # 4. Internal app directory (always works)
            try:
                app_internal_dir = context.getFilesDir()
                paths_to_try.append(('Internal', app_internal_dir))
                print(f"✅ Found Internal: {app_internal_dir.getAbsolutePath()}")
            except Exception as e:
                print(f"⚠️ Could not access Internal: {e}")
            
            # Try each path until one works
            last_error = None
            for path_name, directory in paths_to_try:
                try:
                    print(f"\n🔄 Trying {path_name}...")
                    
                    # Create full path
                    file_obj = File(directory, filename)
                    full_path = file_obj.getAbsolutePath()
                    
                    print(f"💾 Writing to: {full_path}")
                    
                    # Write file
                    self._write_csv_file(full_path, content)
                    print(f"✅ File written successfully!")
                    
                    # Try to notify media scanner
                    self._notify_media_scanner(context, file_obj)
                    
                    # Try to open share dialog
                    try:
                        self._android_share_file(full_path, context)
                        print(f"✅ Share dialog opened")
                    except Exception as share_error:
                        print(f"⚠️ Share dialog failed: {share_error}")
                        # Not critical if share fails
                    
                    # Success!
                    success_path = f"{path_name}/{filename}"
                    if success_callback:
                        success_callback(success_path)
                    
                    return True
                    
                except Exception as e:
                    last_error = e
                    print(f"❌ {path_name} failed: {e}")
                    continue
            
            # All paths failed
            error_msg = f"All export paths failed. Last error: {last_error}"
            print(f"❌ {error_msg}")
            
            if error_callback:
                error_callback(error_msg)
            
            return False
            
        except Exception as e:
            error_msg = f"Android export (after permission) failed: {str(e)}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            
            if error_callback:
                error_callback(error_msg)
            
            return False
    
    def _notify_media_scanner(self, context, file_obj):
        """Notify Android media scanner so file appears in file manager."""
        try:
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            scan_intent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
            file_uri = Uri.fromFile(file_obj)
            scan_intent.setData(file_uri)
            context.sendBroadcast(scan_intent)
            print(f"✅ Media scanner notified")
        except Exception as e:
            print(f"⚠️ Media scanner failed: {e}")
    
    def _android_share_file(self, filepath: str, context):
        """Open Android share dialog for a file."""
        try:
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            String = autoclass('java.lang.String')
            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            
            file_obj = File(filepath)
            
            # Try FileProvider first (Android 7+)
            try:
                print(f"📤 Trying FileProvider...")
                FileProvider = autoclass('androidx.core.content.FileProvider')
                authority = f"{context.getPackageName()}.fileprovider"
                file_uri = FileProvider.getUriForFile(context, authority, file_obj)
                print(f"✅ FileProvider URI: {file_uri.toString()}")
            except Exception as fp_error:
                print(f"⚠️ FileProvider failed: {fp_error}")
                # Fallback to file:// URI (Android 6 and below)
                file_uri = Uri.fromFile(file_obj)
                print(f"⚠️ Using file URI: {file_uri.toString()}")
            
            # Create share intent
            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType(String("text/csv"))
            intent.putExtra(Intent.EXTRA_STREAM, file_uri)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            
            # Create chooser
            chooser = Intent.createChooser(intent, String("Export CSV"))
            chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            
            context.startActivity(chooser)
            
        except Exception as e:
            print(f"❌ Share dialog error: {e}")
            raise
    
    def _export_ios(self, filename: str, content: List[List[str]],
                   success_callback: Optional[callable],
                   error_callback: Optional[callable]) -> bool:
        """Export CSV on iOS using share sheet."""
        try:
            from pyobjus import autoclass
            from pyobjus.dylib_manager import load_framework
            import tempfile
            
            load_framework('/System/Library/Frameworks/UIKit.framework')
            
            UIApplication = autoclass('UIApplication')
            NSURL = autoclass('NSURL')
            NSString = autoclass('NSString')
            UIActivityViewController = autoclass('UIActivityViewController')
            NSArray = autoclass('NSArray')
            
            temp_dir = tempfile.gettempdir()
            full_path = os.path.join(temp_dir, filename)
            self._write_csv_file(full_path, content)
            
            file_url = NSURL.fileURLWithPath_(
                NSString.alloc().initWithUTF8String_(full_path.encode('utf-8'))
            )
            
            items_array = NSArray.arrayWithObject_(file_url)
            activity_vc = UIActivityViewController.alloc() \
                .initWithActivityItems_applicationActivities_(items_array, None)
            
            app = UIApplication.sharedApplication()
            root_vc = app.keyWindow().rootViewController()
            
            if root_vc:
                root_vc.presentViewController_animated_completion_(
                    activity_vc, True, None
                )
                print("✅ iOS share sheet opened")
                
                if success_callback:
                    success_callback(filename)
                
                return True
            
        except Exception as e:
            error_msg = f"iOS export failed: {str(e)}"
            print(f"❌ {error_msg}")
            if error_callback:
                error_callback(error_msg)
            return False
    
    def _export_fallback(self, filename: str, content: List[List[str]],
                        success_callback: Optional[callable],
                        error_callback: Optional[callable]) -> bool:
        """Fallback export method - save to exports directory."""
        try:
            os.makedirs(self.exports_dir, exist_ok=True)
            full_path = os.path.join(self.exports_dir, filename)
            self._write_csv_file(full_path, content)
            
            if success_callback:
                success_callback(full_path)
            
            print(f"✅ CSV exported (fallback): {full_path}")
            return True
            
        except Exception as e:
            error_msg = f"Fallback export failed: {str(e)}"
            print(f"❌ {error_msg}")
            if error_callback:
                error_callback(error_msg)
            return False
    
    def _write_csv_file(self, filepath: str, content: List[List[str]]) -> None:
        """Write CSV content to file."""
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in content:
                writer.writerow(row)