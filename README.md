# File System MCP Server

A powerful file system management server built with FastMCP that provides a comprehensive set of tools for file and directory operations. This server allows you to perform various file system operations through a structured API, making it ideal for automation and integration with other systems.

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
├── data/                    # Data storage directory
│   ├── media/              # Media files
│   ├── cache/              # Cache files
│   ├── temp/               # Temporary files
│   ├── documents/          # Document files
│   ├── userdata/           # User-specific data
│   └── collections/        # File collections
├── fs_server.py            # Main server implementation
├── windows_utils.py        # Windows-specific utilities (optional)
├── media_utils.py          # Media file handling utilities (optional)
├── requirements.txt        # Project dependencies
└── test_prompts_example.md # Example test prompts
```

## Dependencies

### Required Dependencies
- FastMCP
- Pydantic

### Optional Dependencies
The following dependencies are optional and enable additional features:

1. **Windows-specific Features** (`windows_utils.py`)
   - Drive listing
   - Special folders access
   - Windows environment variables
   - Windows system information
   - Windows path validation and normalization

2. **Media File Handling** (`media_utils.py`)
   - Image metadata extraction (requires Pillow)
   - Video metadata extraction (requires ffmpeg-python)
   - Audio metadata extraction (requires mutagen)
   - Thumbnail generation
   - File organization by date

To install optional dependencies:
```bash
pip install Pillow ffmpeg-python mutagen
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

### Setting up with Claude

1. Open Claude's settings:
   - Press `Ctrl+,` (Windows/Linux) or `Cmd+,` (Mac)
   - Or click on the gear icon in the bottom left corner and select "Settings"

2. In the settings search bar, type "mcp"

3. Add the file system server to your MCP servers configuration:
   ```json
   {
     "mcpServers": {
       "file-system": {
         "command": "python",
         "args": [
           "path/to/file-system-mcp-server/fs_server.py"
         ]
       }
     }
   }
   ```
   Replace `path/to/file-system-mcp-server` with the actual path to your installation.

4. Restart Claude to apply the changes

5. You can now use the file system tools by asking Claude to perform file operations.

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

## Error Handling

The server includes comprehensive error handling for:
- Invalid file paths
- File/directory not found
- Permission issues
- Disk space limitations
- Invalid operations

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
