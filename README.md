# File System MCP Server

A comprehensive MCP (Model Context Protocol) server for file system operations, providing Claude and other AI assistants with access to local files and directories.

## Features

- **Cross-platform support** for Windows, macOS, and Linux
- **Comprehensive file operations**: scan, read, write, copy, move, delete
- **Advanced search capabilities**: search by filename or file contents
- **File metadata extraction** for various file types
- **Directory management**: list, create directories
- **Windows-specific features**: drive listing, special folders access
- **Collection management**: group files into collections
- **System information retrieval**

## Supported File Types

The server supports a wide range of file types:

- **Documents**: PDF, TXT, MD, RTF, DOC, DOCX
- **Images**: JPG, PNG, GIF, BMP, TIFF, WEBP
- **Videos**: MP4, AVI, MOV, WMV, MKV, FLV, WEBM
- **Audio**: MP3, WAV, OGG, FLAC, AAC, M4A
- **Code**: PY, JS, HTML, CSS, JAVA, CPP, C, H, CS, PHP, RB, GO, RS, TS
- **Data**: CSV, JSON, XML, YAML, YML, SQL, DB, SQLITE
- **Archives**: ZIP, RAR, 7Z, TAR, GZ, BZ2
- **Spreadsheets**: XLS, XLSX
- **Presentations**: PPT, PPTX
- **Executables**: EXE, MSI, BAT, SH, APP, DMG

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/file-system-mcp-server.git
   cd file-system-mcp-server
   ```

2. Install the required dependencies:
   ```
   pip install mcp
   ```

3. For Windows-specific features (optional):
   ```
   pip install pywin32
   ```

4. For media file metadata extraction (optional):
   ```
   pip install Pillow ffmpeg-python mutagen
   ```

## Usage

1. Start the MCP server:
   ```
   python src/fs_server.py
   ```

2. Configure Claude to use this server by updating your `claude_desktop_config.json` file:

   **Windows:**
   ```json
   {
     "mcpServers": {
       "file-system": {
         "command": "C:/path/to/python.exe",
         "args": [
           "C:/path/to/file-system-mcp-server/src/fs_server.py"
         ]
       }
     }
   }
   ```

   **macOS:**
   ```json
   {
     "mcpServers": {
       "file-system": {
         "command": "/usr/bin/python3",
         "args": [
           "/path/to/file-system-mcp-server/src/fs_server.py"
         ]
       }
     }
   }
   ```

   **Linux:**
   ```json
   {
     "mcpServers": {
       "file-system": {
         "command": "/usr/bin/python3",
         "args": [
           "/path/to/file-system-mcp-server/src/fs_server.py"
         ]
       }
     }
   }
   ```

3. In Claude, you can now use the file system tools by asking Claude to perform file operations.

## Available MCP Tools

The server provides the following MCP tools:

- `scan_directory_tool`: Scan a directory for files
- `get_file_metadata_tool`: Get metadata for a file
- `list_drives`: List available drives (Windows-specific)
- `list_user_directories`: List common user directories
- `read_text_file_tool`: Read a text file
- `write_text_file_tool`: Write or append to a text file
- `search_files_tool`: Search for files by name
- `search_file_contents_tool`: Search within file contents
- `get_system_info`: Get system information
- `copy_file`: Copy a file
- `move_file`: Move a file
- `delete_file`: Delete a file
- `create_directory`: Create a directory
- `list_directory`: List directory contents
- `create_collection`: Create a collection of files

## Testing

Run the test script to verify all tools are working correctly:

```
python src/test_fs_tools.py
```

The test script will:
1. Create a temporary test environment
2. Test each MCP tool
3. Report success or failure for each test
4. Provide a summary of all test results

## Project Structure

```
file-system-mcp-server/
├── src/
│   ├── fs_server.py        # Main MCP server implementation
│   ├── windows_utils.py    # Windows-specific utilities
│   └── test_fs_tools.py    # Test script for MCP tools
├── data/                   # Data directory (created at runtime)
│   ├── media/              # Media files directory
│   ├── cache/              # Cache directory
│   ├── temp/               # Temporary files directory
│   ├── documents/          # Documents directory
│   ├── userdata/           # User data directory
│   └── collections/        # Collections directory
└── README.md               # This file
```

## Cross-Platform Considerations

The server is designed to work across different operating systems:

- **Windows**: Supports drive letters, special folders, and Windows-specific APIs
- **macOS**: Uses appropriate paths and directories
- **Linux**: Follows XDG directory standards

See `CROSS_PLATFORM.md` for detailed information on cross-platform support.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
