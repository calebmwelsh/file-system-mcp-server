# MCP Server Test Prompts

This file contains a collection of prompts to test the functionality of the File System MCP Server.

## File Operations

### Copy Files
```
Copy all files from "source_directory" to "destination_directory"
```

### Collections
```
Create a collection of all images in the "path/to/directory" directory
```

## Directory Operations

### List Directory
```
List the contents of "path/to/directory"
```

### List Directory Recursively
```
Show the complete directory structure of "path/to/directory" in a tree-like format
```

### Create Directory
```
Create a new directory at "path/to/new/directory"
```

### Scan Directory
```
Scan the directory "path/to/directory" recursively for all files
```

## File Operations

### Get File Metadata
```
Get metadata for the file "path/to/file"
```

### Read Text File
```
Read the contents of "path/to/file" (first 50 lines)
```

### Write Text File
```
Write "Hello, this is a test file!" to "path/to/file"
```

### Move File
```
Move the file "path/to/source/file" to "path/to/destination/file"
```

### Delete File
```
Delete the file "path/to/file"
```

## Search Operations

### Search Files
```
Search for files containing "query" in their name in "path/to/directory"
```

### Search File Contents
```
Search for files containing the text "query" in "path/to/directory"
```

## System Information

### List Drives
```
List all available drives on the system
```

### Get System Information
```
Get detailed information about the system
```

### List User Directories
```
List all common user directories on the system
```

## Notes
- Replace all paths in quotes with actual paths on your system
- The server supports both Windows and Unix-style paths
- Some operations may require appropriate permissions
- The recursive directory listing has a default maximum depth of 3 levels 