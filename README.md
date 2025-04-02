# File System MCP Server

A powerful file system management server built with FastMCP that provides a comprehensive set of tools for file and directory operations. This server allows you to perform various file system operations through a structured API, making it ideal for automation and integration with other systems.

## Platform Support

The server is designed to work across different operating systems, but with varying levels of functionality:

### Windows
- Full feature support
- Drive listing
- Special folders access
- Windows-specific path handling
- Detailed system information

### macOS/Linux
- Basic file operations
- Directory operations
- File search and metadata
- Basic system information
- Note: Some Windows-specific features are not available

## Future Implementation

### Planned macOS Support
- Native path handling for macOS
- macOS-specific system information retrieval
- Integration with macOS file system features
- Support for macOS-specific file attributes
- Implementation of macOS-specific utilities (similar to windows_utils.py)

### Planned Linux Support
- Native path handling for Linux
- Linux-specific system information retrieval
- Integration with Linux file system features
- Support for Linux file permissions and attributes
- Implementation of Linux-specific utilities

### Cross-Platform Improvements
- Unified path handling system
- Platform-agnostic drive detection
- Consistent system information API
- Standardized file attributes across platforms
- Cross-platform file system event monitoring
- Universal file collection system

### Timeline
- Phase 1: Basic cross-platform compatibility improvements
- Phase 2: Platform-specific feature implementations
- Phase 3: Advanced cross-platform features
- Phase 4: Performance optimizations and refinements

## Features

### File Operations
- Copy files with backup support
- Move files with backup support
- Delete files with safety checks
- Read file contents
- Write file contents
- Get file information (size, creation time, modification time)
- Search files by name pattern
- Create file collections for organizing related files

### Directory Operations
- List directory contents
- Create directories
- Delete directories
- List directories recursively (tree-like structure)
- Search directories by name pattern

### System Information
- Get system information (OS, CPU, memory, disk usage)
- Get disk information (total space, used space, free space)
- Get directory information (file count, total size)

## Project Structure

```
file-system-mcp-server/
├── fs_server.py            # Main server implementation
├── windows_utils.py        # Windows-specific utilities (Windows only)
├── requirements.txt        # Project dependencies
└── test_prompts_example.md # Example test prompts
```

### Collections Storage

Collections can be stored in any directory specified by the user. If no storage location is specified, collections will be stored in a default location within the project's `data/collections` directory.

Example usage:
```python
# Store in default location
create_collection("my_collection", ["file1.txt", "file2.txt"])

# Store in custom location
create_collection("my_collection", ["file1.txt", "file2.txt"], storage_path="/path/to/store")
```

## Dependencies

### Required Dependencies
- FastMCP
- Pydantic
- pywin32 (Windows only)
- WMI (Windows only)

To install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/calebmwelsh/file-system-mcp-server.git
cd file-system-mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

For detailed MCP configuration instructions across different development environments (Claude, Cursor, Windsurf), visit:
[MCP Configuration Guide](https://calebmwelsh.github.io/Configure-MCP/)

### Integration with Claude

To integrate the File System MCP server with Claude, add the following to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "file-system": {
      "command": "/absolute/path/to/python",
      "args": [
        "/absolute/path/to/file-system-mcp-server/fs_server.py"
      ]
    }
  }
}
```

#### Finding Your Python Path

To find your Python executable path, use the following command:

**Windows (PowerShell):**
```powershell
(Get-Command python).Source
```

**Windows (Command Prompt/Terminal):**
```cmd
where python
```

**Linux/macOS (Terminal):**
```bash
which python
```

Replace `/absolute/path/to/python` with the output from the appropriate command above.

#### Example Configuration

For Windows, your configuration might look like this:
```json
{
  "mcpServers": {
    "file-system": {
      "command": "C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Python\\Python39\\python.exe",
      "args": [
        "C:\\Users\\YourUsername\\Documents/file-system-mcp-server/fs_server.py"
      ]
    }
  }
}
```

For macOS/Linux:
```json
{
  "mcpServers": {
    "file-system": {
      "command": "/usr/local/bin/python3",
      "args": [
        "/Users/YourUsername/Documents/file-system-mcp-server/fs_server.py"
      ]
    }
  }
}
```

After adding the configuration:
1. Save the `claude_desktop_config.json` file
2. Restart Claude
3. You can now use the file system tools by asking Claude to perform file operations

## Available Tools

### File Operations
- `copy_file`: Copy a file with optional backup
- `move_file`: Move a file with optional backup
- `delete_file`: Delete a file with safety checks
- `read_file`: Read file contents
- `write_file`: Write contents to a file
- `get_file_info`: Get detailed file information
- `search_files`: Search files by name pattern
- `create_collection`: Create a collection of files

### Directory Operations
- `list_directory`: List directory contents
- `create_directory`: Create a new directory
- `delete_directory`: Delete a directory
- `list_directory_recursively`: Show directory structure in tree format
- `search_directories`: Search directories by name pattern

### System Information
- `get_system_info`: Get system information
- `get_disk_info`: Get disk usage information
- `get_directory_info`: Get directory statistics

## Known Issues

The following features are currently experiencing issues and may not work as expected:

1. **Delete File Function**
   - The `delete_file` function may fail to properly delete files in some cases
   - Users are advised to verify file deletion manually or use alternative methods when critical
   - Issue is under investigation and will be fixed in a future update

2. **List Drives Function**
   - The `list_drives` function may not correctly detect or display all available drives
   - Some drives may be missing from the list or show incorrect information
   - This is a known limitation and will be addressed in future updates

3. **Platform-Specific Limitations**
   - Windows-specific features are not available on macOS/Linux
   - Some path handling may differ between platforms
   - System information retrieval varies by platform

## Error Handling

The server includes comprehensive error handling for:
- Invalid file paths
- File/directory not found
- Permission issues
- Disk space limitations
- Invalid operations
- Platform-specific errors

## Security

- All file operations include path validation
- Backup files are created before destructive operations
- System information access is restricted to safe operations
- File operations are performed with proper error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with FastMCP
- Uses Pydantic for data validation
- Inspired by modern file system management tools
