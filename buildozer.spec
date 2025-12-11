# Key Android settings for CSV export

# Add androidx support (required for FileProvider)
android.gradle_dependencies = androidx.appcompat:appcompat:1.3.1,androidx.core:core:1.6.0

# Enable AndroidX
android.enable_androidx = True

# Add FileProvider to AndroidManifest.xml
android.manifest.application = """
    <provider
        android:name="androidx.core.content.FileProvider"
        android:authorities="${applicationId}.fileprovider"
        android:exported="false"
        android:grantUriPermissions="true">
        <meta-data
            android:name="android.support.FILE_PROVIDER_PATHS"
            android:resource="@xml/fileprovider_paths" />
    </provider>
"""

# Create the fileprovider_paths.xml resource
android.add_resources = fileprovider_paths.xml:xml

# Permissions (optional - we use app cache, no permissions needed)
# But good to have for potential future use
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.meta_data = android.support.FILE_PROVIDER_PATHS=@xml/file_paths