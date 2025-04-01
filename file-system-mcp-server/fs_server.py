import os
import subprocess
import tempfile
import platform
import json
import shutil
from pathlib import Path
import mimetypes
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP()

# Determine the operating system
SYSTEM = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'

# Get the project root directory (parent of src directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Set up base directories within the project
BASE_DIR = os.path.join(PROJECT_ROOT, "data")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DOCS_DIR = os.path.join(BASE_DIR, "documents")
DATA_DIR = os.path.join(BASE_DIR, "userdata")
COLLECTIONS_DIR = os.path.join(BASE_DIR, "collections")

# Create necessary directories if they don't exist
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(COLLECTIONS_DIR, exist_ok=True)

# Initialize mimetypes
mimetypes.init()

# Import platform-specific utilities
if SYSTEM == "Windows":
    try:
        from windows_utils import (
            get_windows_drives,
            get_windows_special_folders,
            get_windows_environment,
            get_windows_system_info,
            normalize_windows_path,
            is_valid_windows_path
        )
    except ImportError:
        print("Windows utilities could not be imported. Some features may be limited.")

# Helper functions
def get_file_type(file_path):
    """Determine the type of file based on its extension or mimetype."""
    mime_type, _ = mimetypes.guess_type(file_path)
    
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('text/'):
            return 'text'
        elif mime_type.startswith('application/pdf'):
            return 'pdf'
        elif mime_type.startswith('application/msword') or mime_type.startswith('application/vnd.openxmlformats-officedocument.wordprocessingml'):
            return 'document'
        elif mime_type.startswith('application/vnd.ms-excel') or mime_type.startswith('application/vnd.openxmlformats-officedocument.spreadsheetml'):
            return 'spreadsheet'
        elif mime_type.startswith('application/vnd.ms-powerpoint') or mime_type.startswith('application/vnd.openxmlformats-officedocument.presentationml'):
            return 'presentation'
    
    # Fallback to extension-based detection
    ext = os.path.splitext(file_path)[1].lower()
    
    # Common image extensions
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
        return 'image'
    # Common video extensions
    elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm']:
        return 'video'
    # Common audio extensions
    elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']:
        return 'audio'
    # Common document extensions
    elif ext in ['.pdf', '.txt', '.md', '.rtf']:
        return 'document'
    # Common code extensions
    elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.ts']:
        return 'code'
    # Common data extensions
    elif ext in ['.csv', '.json', '.xml', '.yaml', '.yml', '.sql', '.db', '.sqlite']:
        return 'data'
    # Common archive extensions
    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
        return 'archive'
    # Common executable extensions
    elif ext in ['.exe', '.msi', '.bat', '.sh', '.app', '.dmg']:
        return 'executable'
    # Microsoft Office extensions
    elif ext in ['.doc', '.docx']:
        return 'document'
    elif ext in ['.xls', '.xlsx']:
        return 'spreadsheet'
    elif ext in ['.ppt', '.pptx']:
        return 'presentation'
    
    return 'unknown'

def get_file_metadata(file_path):
    """Get metadata for a file."""
    try:
        stat_info = os.stat(file_path)
        file_size = stat_info.st_size
        created_time = datetime.fromtimestamp(stat_info.st_ctime)
        modified_time = datetime.fromtimestamp(stat_info.st_mtime)
        
        file_type = get_file_type(file_path)
        
        metadata = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": file_size,
            "created": created_time.isoformat(),
            "modified": modified_time.isoformat(),
            "type": file_type
        }
        
        # For text files, include a preview
        if file_type in ['text', 'code', 'document'] and os.path.splitext(file_path)[1].lower() in ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.ts']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    # Read first 1000 characters as preview
                    preview = f.read(1000)
                    if len(preview) == 1000:
                        preview += "... (truncated)"
                    metadata["preview"] = preview
                    
                    # Count lines
                    f.seek(0)
                    line_count = sum(1 for _ in f)
                    metadata["line_count"] = line_count
            except Exception as e:
                metadata["preview_error"] = str(e)
        
        return metadata
    except Exception as e:
        return {"error": str(e)}

def scan_directory(directory_path, recursive=True, file_types=None):
    """Scan a directory for files."""
    results = []
    
    try:
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_type = get_file_type(file_path)
                    
                    if file_types is None or file_type in file_types:
                        metadata = get_file_metadata(file_path)
                        results.append(metadata)
        else:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    file_type = get_file_type(item_path)
                    
                    if file_types is None or file_type in file_types:
                        metadata = get_file_metadata(item_path)
                        results.append(metadata)
    except Exception as e:
        return {"error": str(e)}
    
    return results

def read_text_file(file_path, max_lines=None):
    """Read a text file and return its contents."""
    try:
        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_type = get_file_type(file_path)
        if file_type not in ['text', 'code', 'document']:
            return {"error": f"Not a text file: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            if max_lines:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line)
                content = ''.join(lines)
                if i >= max_lines:
                    content += f"\n... (truncated, showing {max_lines} of {i+1}+ lines)"
            else:
                content = f.read()
        
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "content": content,
            "size": os.path.getsize(file_path)
        }
    except Exception as e:
        return {"error": str(e)}

def write_text_file(file_path, content, append=False):
    """Write content to a text file."""
    try:
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "mode": "append" if append else "write"
        }
    except Exception as e:
        return {"error": str(e)}

def search_files(directory_path, query, recursive=True, file_types=None):
    """Search for files matching a query in a directory."""
    results = []
    
    try:
        query = query.lower()
        
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if query in file.lower():
                        file_path = os.path.join(root, file)
                        file_type = get_file_type(file_path)
                        
                        if file_types is None or file_type in file_types:
                            metadata = get_file_metadata(file_path)
                            results.append(metadata)
        else:
            for item in os.listdir(directory_path):
                if query in item.lower() and os.path.isfile(os.path.join(directory_path, item)):
                    file_path = os.path.join(directory_path, item)
                    file_type = get_file_type(file_path)
                    
                    if file_types is None or file_type in file_types:
                        metadata = get_file_metadata(file_path)
                        results.append(metadata)
    except Exception as e:
        return {"error": str(e)}
    
    return results

def search_file_contents(directory_path, query, recursive=True, file_types=None, max_results=100):
    """Search for files containing a query in their contents."""
    results = []
    count = 0
    
    try:
        query = query.lower()
        searchable_types = ['text', 'code', 'document']
        searchable_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.cs', '.php', '.rb', '.go', '.rs', '.ts']
        
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if count >= max_results:
                        break
                    
                    file_path = os.path.join(root, file)
                    file_type = get_file_type(file_path)
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    if (file_types is None or file_type in file_types) and (file_type in searchable_types or ext in searchable_extensions):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query in content.lower():
                                    metadata = get_file_metadata(file_path)
                                    
                                    # Add context around the match
                                    index = content.lower().find(query)
                                    start = max(0, index - 50)
                                    end = min(len(content), index + len(query) + 50)
                                    
                                    # Find line number
                                    line_number = content[:index].count('\n') + 1
                                    
                                    metadata["match"] = {
                                        "context": content[start:end],
                                        "line": line_number
                                    }
                                    
                                    results.append(metadata)
                                    count += 1
                        except Exception:
                            # Skip files that can't be read as text
                            pass
        else:
            for item in os.listdir(directory_path):
                if count >= max_results:
                    break
                
                file_path = os.path.join(directory_path, item)
                if os.path.isfile(file_path):
                    file_type = get_file_type(file_path)
                    ext = os.path.splitext(file_path)[1].lower()
                    
                    if (file_types is None or file_type in file_types) and (file_type in searchable_types or ext in searchable_extensions):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query in content.lower():
                                    metadata = get_file_metadata(file_path)
                                    
                                    # Add context around the match
                                    index = content.lower().find(query)
                                    start = max(0, index - 50)
                                    end = min(len(content), index + len(query) + 50)
                                    
                                    # Find line number
                                    line_number = content[:index].count('\n') + 1
                                    
                                    metadata["match"] = {
                                        "context": content[start:end],
                                        "line": line_number
                                    }
                                    
                                    results.append(metadata)
                                    count += 1
                        except Exception:
                            # Skip files that can't be read as text
                            pass
    except Exception as e:
        return {"error": str(e)}
    
    return results

# MCP Tool: Scan Directory
@mcp.tool()
def scan_directory_tool(directory_path: str, recursive: bool = True, file_types: list = None):
    """
    Scan a directory for files.
    
    Args:
        directory_path: The path to the directory to scan
        recursive: Whether to scan subdirectories recursively
        file_types: List of file types to include (image, video, audio, document, code, data, etc.)
    
    Returns:
        A list of files with metadata
    """
    # Validate and normalize the directory path
    if SYSTEM == "Windows":
        # Handle Windows-specific path issues
        directory_path = os.path.normpath(directory_path)
    
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        return {"error": f"Directory not found: {directory_path}"}
    
    # Scan the directory
    results = scan_directory(directory_path, recursive, file_types)
    
    return {
        "directory": directory_path,
        "file_count": len(results) if isinstance(results, list) else 0,
        "files": results
    }

# MCP Tool: Get File Metadata
@mcp.tool()
def get_file_metadata_tool(file_path: str):
    """
    Get metadata for a file.
    
    Args:
        file_path: The path to the file
    
    Returns:
        Metadata for the file
    """
    # Validate and normalize the file path
    if SYSTEM == "Windows":
        # Handle Windows-specific path issues
        file_path = os.path.normpath(file_path)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return {"error": f"File not found: {file_path}"}
    
    # Get the file metadata
    metadata = get_file_metadata(file_path)
    
    return metadata

# MCP Tool: List Drives (Windows-specific)
@mcp.tool()
def list_drives():
    """
    List available drives on Windows.
    
    Returns:
        A list of available drives
    """
    if SYSTEM != "Windows":
        return {"error": "This function is only available on Windows"}
    
    try:
        if 'get_windows_drives' in globals():
            return get_windows_drives()
        
        import win32api
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        
        drive_info = []
        for drive in drives:
            try:
                drive_type = win32api.GetDriveType(drive)
                type_name = {
                    0: "Unknown",
                    1: "No Root Directory",
                    2: "Removable",
                    3: "Fixed",
                    4: "Network",
                    5: "CD-ROM",
                    6: "RAM Disk"
                }.get(drive_type, "Unknown")
                
                drive_info.append({
                    "path": drive,
                    "type": type_name
                })
            except:
                pass
        
        return {"drives": drive_info}
    except ImportError:
        return {"error": "win32api module not available. Install pywin32 package."}
    except Exception as e:
        return {"error": str(e)}

# MCP Tool: Create Collection
@mcp.tool()
def create_collection(name: str, file_paths: list):
    """
    Create a collection of files.
    
    Args:
        name: The name of the collection
        file_paths: List of file paths to include in the collection
    
    Returns:
        Information about the created collection
    """
    collection_dir = os.path.join(COLLECTIONS_DIR, name)
    os.makedirs(collection_dir, exist_ok=True)
    
    collection_info = {
        "name": name,
        "created": datetime.now().isoformat(),
        "files": []
    }
    
    for file_path in file_paths:
        if os.path.isfile(file_path):
            file_name = os.path.basename(file_path)
            metadata = get_file_metadata(file_path)
            collection_info["files"].append(metadata)
    
    # Save collection info
    with open(os.path.join(collection_dir, "collection.json"), "w") as f:
        json.dump(collection_info, f, indent=2)
    
    return {
        "collection": name,
        "file_count": len(collection_info["files"]),
        "path": collection_dir
    }

# MCP Tool: List User Directories
@mcp.tool()
def list_user_directories():
    """
    List common user directories based on the operating system.
    
    Returns:
        A list of common user directories
    """
    directories = {}
    
    if SYSTEM == "Windows":
        # Windows user directories
        for dir_name in ["Desktop", "Documents", "Pictures", "Videos", "Music", "Downloads", "AppData"]:
            path = os.path.join(os.path.expanduser("~"), dir_name)
            if os.path.isdir(path):
                directories[dir_name] = path
        
        # Windows special folders if available
        if 'get_windows_special_folders' in globals():
            try:
                special_folders = get_windows_special_folders()
                if isinstance(special_folders, dict) and "special_folders" in special_folders:
                    directories.update(special_folders["special_folders"])
            except Exception:
                pass
    
    elif SYSTEM == "Darwin":  # macOS
        # macOS user directories
        for dir_name, folder in [
            ("Desktop", "Desktop"),
            ("Documents", "Documents"),
            ("Pictures", "Pictures"),
            ("Movies", "Movies"),
            ("Music", "Music"),
            ("Downloads", "Downloads"),
            ("Applications", "Applications"),
            ("Library", "Library")
        ]:
            path = os.path.join(os.path.expanduser("~"), folder)
            if os.path.isdir(path):
                directories[dir_name] = path
    
    else:  # Linux
        # Linux user directories (using XDG)
        try:
            import subprocess
            for dir_name, xdg_key in [
                ("Desktop", "DESKTOP"),
                ("Documents", "DOCUMENTS"),
                ("Pictures", "PICTURES"),
                ("Videos", "VIDEOS"),
                ("Music", "MUSIC"),
                ("Downloads", "DOWNLOAD"),
                ("Templates", "TEMPLATES"),
                ("Public", "PUBLICSHARE")
            ]:
                try:
                    path = subprocess.check_output(
                        ["xdg-user-dir", xdg_key], 
                        universal_newlines=True
                    ).strip()
                    if os.path.isdir(path):
                        directories[dir_name] = path
                except:
                    # Fallback to standard directories
                    path = os.path.join(os.path.expanduser("~"), dir_name)
                    if os.path.isdir(path):
                        directories[dir_name] = path
        except:
            # Fallback if xdg-user-dir is not available
            for dir_name in ["Desktop", "Documents", "Pictures", "Videos", "Music", "Downloads"]:
                path = os.path.join(os.path.expanduser("~"), dir_name)
                if os.path.isdir(path):
                    directories[dir_name] = path
    
    return {"directories": directories}

# MCP Tool: Read Text File
@mcp.tool()
def read_text_file_tool(file_path: str, max_lines: int = None):
    """
    Read a text file and return its contents.
    
    Args:
        file_path: The path to the text file
        max_lines: Maximum number of lines to read (None for all)
    
    Returns:
        The contents of the text file
    """
    # Validate and normalize the file path
    if SYSTEM == "Windows":
        # Handle Windows-specific path issues
        file_path = os.path.normpath(file_path)
    
    return read_text_file(file_path, max_lines)

# MCP Tool: Write Text File
@mcp.tool()
def write_text_file_tool(file_path: str, content: str, append: bool = False):
    """
    Write content to a text file.
    
    Args:
        file_path: The path to the text file
        content: The content to write
        append: Whether to append to the file (True) or overwrite it (False)
    
    Returns:
        Information about the written file
    """
    # Validate and normalize the file path
    if SYSTEM == "Windows":
        # Handle Windows-specific path issues
        file_path = os.path.normpath(file_path)
    
    return write_text_file(file_path, content, append)

# MCP Tool: Search Files
@mcp.tool()
def search_files_tool(directory_path: str, query: str, recursive: bool = True, file_types: list = None):
    """
    Search for files matching a query in a directory.
    
    Args:
        directory_path: The path to the directory to search
        query: The search query (matches file names)
        recursive: Whether to search subdirectories recursively
        file_types: List of file types to include (image, video, audio, document, code, data, etc.)
    
    Returns:
        A list of matching files with metadata
    """
    # Validate and normalize the directory path
    if SYSTEM == "Windows":
        # Handle Windows-specific path issues
        directory_path = os.path.normpath(directory_path)
    
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        return {"error": f"Directory not found: {directory_path}"}
    
    # Search the directory
    results = search_files(directory_path, query, recursive, file_types)
    
    return {
        "directory": directory_path,
        "query": query,
        "match_count": len(results) if isinstance(results, list) else 0,
        "matches": results
    }

# MCP Tool: Search File Contents
@mcp.tool()
def search_file_contents_tool(directory_path: str, query: str, recursive: bool = True, file_types: list = None, max_results: int = 100):
    """
    Search for files containing a query in their contents.
    
    Args:
        directory_path: The path to the directory to search
        query: The search query (matches file contents)
        recursive: Whether to search subdirectories recursively
        file_types: List of file types to include (text, code, document)
        max_results: Maximum number of results to return
    
    Returns:
        A list of matching files with metadata and context
    """
    # Validate and normalize the directory path
    if SYSTEM == "Windows":
        # Handle Windows-specific path issues
        directory_path = os.path.normpath(directory_path)
    
    # Check if the directory exists
    if not os.path.isdir(directory_path):
        return {"error": f"Directory not found: {directory_path}"}
    
    # Search the directory
    results = search_file_contents(directory_path, query, recursive, file_types, max_results)
    
    return {
        "directory": directory_path,
        "query": query,
        "match_count": len(results) if isinstance(results, list) else 0,
        "matches": results
    }

# MCP Tool: Get System Information
@mcp.tool()
def get_system_info():
    """
    Get information about the system.
    
    Returns:
        System information
    """
    try:
        # Basic system information
        info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "user_home": os.path.expanduser("~")
        }
        
        # Windows-specific information
        if SYSTEM == "Windows" and 'get_windows_system_info' in globals():
            try:
                windows_info = get_windows_system_info()
                if isinstance(windows_info, dict) and "system_info" in windows_info:
                    info.update(windows_info)
            except Exception as e:
                info["windows_error"] = str(e)
        
        # Get environment variables
        if SYSTEM == "Windows" and 'get_windows_environment' in globals():
            try:
                env_info = get_windows_environment()
                if isinstance(env_info, dict) and "environment" in env_info:
                    info["environment"] = env_info["environment"]
            except Exception as e:
                info["environment_error"] = str(e)
        
        return {"system_info": info}
    except Exception as e:
        return {"error": str(e)}

# MCP Tool: Copy File
@mcp.tool()
def copy_file(source_path: str, destination_path: str, overwrite: bool = False):
    """
    Copy a file from source to destination.
    
    Args:
        source_path: The path to the source file
        destination_path: The path to the destination file
        overwrite: Whether to overwrite the destination file if it exists
    
    Returns:
        Information about the copied file
    """
    try:
        # Validate and normalize the paths
        if SYSTEM == "Windows":
            source_path = os.path.normpath(source_path)
            destination_path = os.path.normpath(destination_path)
        
        # Check if the source file exists
        if not os.path.isfile(source_path):
            return {"error": f"Source file not found: {source_path}"}
        
        # Check if the destination file exists
        if os.path.exists(destination_path) and not overwrite:
            return {"error": f"Destination file already exists: {destination_path}"}
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        
        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "size": os.path.getsize(destination_path)
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Tool: Move File
@mcp.tool()
def move_file(source_path: str, destination_path: str, overwrite: bool = False):
    """
    Move a file from source to destination.
    
    Args:
        source_path: The path to the source file
        destination_path: The path to the destination file
        overwrite: Whether to overwrite the destination file if it exists
    
    Returns:
        Information about the moved file
    """
    try:
        # Validate and normalize the paths
        if SYSTEM == "Windows":
            source_path = os.path.normpath(source_path)
            destination_path = os.path.normpath(destination_path)
        
        # Check if the source file exists
        if not os.path.isfile(source_path):
            return {"error": f"Source file not found: {source_path}"}
        
        # Check if the destination file exists
        if os.path.exists(destination_path) and not overwrite:
            return {"error": f"Destination file already exists: {destination_path}"}
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        
        # Move the file
        shutil.move(source_path, destination_path)
        
        return {
            "success": True,
            "source": source_path,
            "destination": destination_path,
            "size": os.path.getsize(destination_path)
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Tool: Delete File
@mcp.tool()
def delete_file(file_path: str):
    """
    Delete a file.
    
    Args:
        file_path: The path to the file to delete
    
    Returns:
        Information about the deleted file
    """
    try:
        # Validate and normalize the path
        if SYSTEM == "Windows":
            file_path = os.path.normpath(file_path)
        
        # Check if the file exists
        if not os.path.isfile(file_path):
            return {"error": f"File not found: {file_path}"}
        
        # Get file info before deletion
        file_info = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size": os.path.getsize(file_path)
        }
        
        # Delete the file
        os.remove(file_path)
        
        return {
            "success": True,
            "deleted_file": file_info
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Tool: Create Directory
@mcp.tool()
def create_directory(directory_path: str):
    """
    Create a directory.
    
    Args:
        directory_path: The path to the directory to create
    
    Returns:
        Information about the created directory
    """
    try:
        # Validate and normalize the path
        if SYSTEM == "Windows":
            directory_path = os.path.normpath(directory_path)
        
        # Create the directory
        os.makedirs(directory_path, exist_ok=True)
        
        return {
            "success": True,
            "path": directory_path
        }
    except Exception as e:
        return {"error": str(e)}

# MCP Tool: List Directory
@mcp.tool()
def list_directory(directory_path: str):
    """
    List the contents of a directory.
    
    Args:
        directory_path: The path to the directory to list
    
    Returns:
        A list of files and directories in the directory
    """
    try:
        # Validate and normalize the path
        if SYSTEM == "Windows":
            directory_path = os.path.normpath(directory_path)
        
        # Check if the directory exists
        if not os.path.isdir(directory_path):
            return {"error": f"Directory not found: {directory_path}"}
        
        # List the directory contents
        items = os.listdir(directory_path)
        
        files = []
        directories = []
        
        for item in items:
            item_path = os.path.join(directory_path, item)
            
            if os.path.isfile(item_path):
                files.append({
                    "name": item,
                    "path": item_path,
                    "size": os.path.getsize(item_path),
                    "type": get_file_type(item_path)
                })
            elif os.path.isdir(item_path):
                directories.append({
                    "name": item,
                    "path": item_path
                })
        
        return {
            "path": directory_path,
            "files": files,
            "directories": directories,
            "file_count": len(files),
            "directory_count": len(directories)
        }
    except Exception as e:
        return {"error": str(e)}

# Start the MCP server
if __name__ == "__main__":
    print(f"File System MCP Server starting...")
    print(f"Operating System: {SYSTEM}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Base Directory: {BASE_DIR}")
    mcp.run()
