# Cross-Platform Considerations for Local Media MCP Server

This document outlines the key considerations and implementation details for ensuring the Local Media MCP Server works effectively across Windows, macOS, and Linux operating systems.

## File System Differences

### Path Separators
- **Windows**: Uses backslash (`\`) as path separator
- **macOS/Linux**: Use forward slash (`/`) as path separator

Our implementation handles this by:
- Using `os.path.join()` for path construction
- Normalizing paths with `os.path.normpath()`
- In Windows-specific code, providing additional path normalization via `normalize_windows_path()`

### Base Directories
- **Windows**: `%USERPROFILE%\LocalMediaMCP\`
- **macOS**: `~/Library/Application Support/LocalMediaMCP/`
- **Linux**: `~/.local/share/LocalMediaMCP/`

These differences are handled in `media_server.py` with platform-specific path construction.

## Drive and Directory Structure

### Drive Access
- **Windows**: Has drive letters (C:, D:, etc.) and uses `win32api.GetLogicalDriveStrings()`
- **macOS**: Uses volumes mounted at `/Volumes/`
- **Linux**: Uses mount points under `/mnt/` or `/media/`

The `list_drives()` function is implemented with Windows-specific code and provides appropriate feedback on other platforms.

### Special Folders
- **Windows**: Uses special folder names like "My Documents", "My Pictures"
- **macOS**: Uses standard folders like "Documents", "Pictures"
- **Linux**: Uses XDG directories

The `list_user_directories()` function detects the platform and returns appropriate directories.

## Dependencies

### Windows-Specific Dependencies
- **PyWin32**: Required for Windows drive listing and special folder access
- **WMI**: Optional for detailed system information

### Cross-Platform Dependencies
- **Pillow**: For image processing
- **ffmpeg-python**: For video processing
- **mutagen**: For audio metadata

The code gracefully handles missing dependencies with informative error messages.

## Media File Handling

### File Type Detection
- Uses file extensions as a fallback
- Implements signature-based detection for better accuracy
- Handles platform-specific file associations

### Thumbnail Generation
- Uses Pillow for images across all platforms
- Uses ffmpeg for videos across all platforms
- Stores thumbnails in platform-appropriate locations

## Performance Considerations

### Windows
- File system operations can be slower on Windows, especially with antivirus scanning
- Network drives may have additional latency
- UNC paths require special handling

### macOS
- Case-insensitive file system by default
- Resource forks and extended attributes
- Spotlight integration for potential performance improvements

### Linux
- Case-sensitive file system
- Various file systems (ext4, btrfs, etc.) with different performance characteristics
- Desktop environment integration varies

## Security and Permissions

### Windows
- User Account Control (UAC) may restrict access to certain directories
- NTFS permissions model
- Special handling for administrative privileges

### macOS
- Sandboxing restrictions in newer macOS versions
- File system permissions based on Unix model
- Privacy protections requiring user consent for accessing certain directories

### Linux
- Standard Unix permissions model
- AppArmor or SELinux may restrict access
- Different desktop environments have different file access dialogs

## Integration with Claude

### Configuration
The `claude_desktop_config.json` file needs platform-specific paths:

**Windows:**
```json
{
  "mcpServers": {
    "local-media-server": {
      "command": "C:/path/to/python.exe",
      "args": [
        "C:/path/to/local-media-mcp-server/src/media_server.py"
      ]
    }
  }
}
```

**macOS:**
```json
{
  "mcpServers": {
    "local-media-server": {
      "command": "/usr/bin/python3",
      "args": [
        "/path/to/local-media-mcp-server/src/media_server.py"
      ]
    }
  }
}
```

**Linux:**
```json
{
  "mcpServers": {
    "local-media-server": {
      "command": "/usr/bin/python3",
      "args": [
        "/path/to/local-media-mcp-server/src/media_server.py"
      ]
    }
  }
}
```

## Testing Recommendations

### Windows Testing
- Test on multiple Windows versions (10, 11)
- Test with different drive configurations (local, network, removable)
- Test with various permission scenarios

### macOS Testing
- Test on recent macOS versions
- Test with privacy protection enabled
- Test with different file system formats

### Linux Testing
- Test on major distributions (Ubuntu, Fedora, etc.)
- Test with different desktop environments (GNOME, KDE)
- Test with different file managers

## Future Enhancements

### Windows-Specific
- Integration with Windows Search for faster file discovery
- Windows Media Player library integration
- OneDrive integration

### macOS-Specific
- Photos app integration
- iCloud integration
- Spotlight search integration

### Linux-Specific
- Tracker/Baloo integration for desktop search
- KDE/GNOME media collection integration
- Thumbnail caching using desktop environment standards
