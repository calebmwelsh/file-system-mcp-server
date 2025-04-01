import json
import mimetypes
import os
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# Initialize the MCP server
mcp = FastMCP()

# Determine the operating system
SYSTEM = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'

# Get the project root directory (parent of src directory)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Set up default directories within the project
DEFAULT_BASE_DIR = os.path.join(PROJECT_ROOT, "data")
DEFAULT_COLLECTIONS_DIR = os.path.join(DEFAULT_BASE_DIR, "collections")

# Create default directories if they don't exist
os.makedirs(DEFAULT_BASE_DIR, exist_ok=True)
os.makedirs(DEFAULT_COLLECTIONS_DIR, exist_ok=True)

# Initialize mimetypes
mimetypes.init()

# Import platform-specific utilities
if SYSTEM == "Windows":
    try:
        from windows_utils import (
            get_windows_drives,
            get_windows_environment,
            get_windows_special_folders,
            get_windows_system_info,
            is_valid_windows_path,
            normalize_windows_path,
        )
    except ImportError:
        print("Windows utilities could not be imported. Some features may be limited.")

# Pydantic models for request and response validation
class FileMetadata(BaseModel):
    path: str
    name: str
    size: int
    created: str
    modified: str
    type: str
    preview: Optional[str] = None
    line_count: Optional[int] = None
    preview_error: Optional[str] = None
    error: Optional[str] = None

class FileContent(BaseModel):
    path: str
    name: str
    content: str
    size: int
    error: Optional[str] = None

class FileWriteResult(BaseModel):
    success: bool
    path: str
    name: str
    size: int
    mode: str
    error: Optional[str] = None

class FileMatch(BaseModel):
    context: str
    line: int

class FileSearchResult(BaseModel):
    path: str
    name: str
    size: int
    created: str
    modified: str
    type: str
    match: Optional[FileMatch] = None
    error: Optional[str] = None

class DirectoryItem(BaseModel):
    name: str
    path: str

class FileItem(BaseModel):
    name: str
    path: str
    size: int
    type: str

class DirectoryListing(BaseModel):
    path: str
    files: List[FileItem]
    directories: List[DirectoryItem]
    file_count: int
    directory_count: int
    error: Optional[str] = None

class DriveInfo(BaseModel):
    path: str
    type: str

class DriveListing(BaseModel):
    drives: List[DriveInfo]
    error: Optional[str] = None

class CollectionResult(BaseModel):
    collection: str
    file_count: int
    path: str
    error: Optional[str] = None

class SystemInfo(BaseModel):
    system: str
    node: str
    release: str
    version: str
    machine: str
    processor: str
    python_version: str
    user_home: str
    windows_error: Optional[str] = None
    environment_error: Optional[str] = None

class SystemInfoResult(BaseModel):
    system_info: SystemInfo
    error: Optional[str] = None

class FileCopyResult(BaseModel):
    success: bool
    source: str
    destination: str
    size: int
    error: Optional[str] = None

class FileMoveResult(BaseModel):
    success: bool
    source: str
    destination: str
    size: int
    error: Optional[str] = None

class FileDeleteInfo(BaseModel):
    path: str
    name: str
    size: int

class FileDeleteResult(BaseModel):
    success: bool
    deleted_file: FileDeleteInfo
    error: Optional[str] = None

class DirectoryCreateResult(BaseModel):
    success: bool
    path: str
    error: Optional[str] = None

class ScanDirectoryResult(BaseModel):
    directory: str
    file_count: int
    files: List[FileMetadata]
    error: Optional[str] = None

class SearchFilesResult(BaseModel):
    directory: str
    query: str
    match_count: int
    matches: List[FileMetadata]
    error: Optional[str] = None

class SearchFileContentsResult(BaseModel):
    directory: str
    query: str
    match_count: int
    matches: List[FileSearchResult]
    error: Optional[str] = None

class UserDirectoriesResult(BaseModel):
    directories: Dict[str, str]
    error: Optional[str] = None

class RecursiveDirectoryListing(BaseModel):
    path: str
    structure: str
    file_count: int
    directory_count: int
    error: Optional[str] = None

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
        
        return FileMetadata(**metadata)
    except Exception as e:
        return FileMetadata(
            path=file_path,
            name=os.path.basename(file_path),
            size=0,
            created=datetime.now().isoformat(),
            modified=datetime.now().isoformat(),
            type="unknown",
            error=str(e)
        )

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
            return FileContent(
                path=file_path,
                name=os.path.basename(file_path),
                content="",
                size=0,
                error=f"File not found: {file_path}"
            )
        
        file_type = get_file_type(file_path)
        if file_type not in ['text', 'code', 'document']:
            return FileContent(
                path=file_path,
                name=os.path.basename(file_path),
                content="",
                size=os.path.getsize(file_path),
                error=f"Not a text file: {file_path}"
            )
        
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
        
        return FileContent(
            path=file_path,
            name=os.path.basename(file_path),
            content=content,
            size=os.path.getsize(file_path)
        )
    except Exception as e:
        return FileContent(
            path=file_path,
            name=os.path.basename(file_path),
            content="",
            size=0,
            error=str(e)
        )

def write_text_file(file_path, content, append=False):
    """Write content to a text file."""
    try:
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        
        return FileWriteResult(
            success=True,
            path=file_path,
            name=os.path.basename(file_path),
            size=os.path.getsize(file_path),
            mode="append" if append else "write"
        )
    except Exception as e:
        return FileWriteResult(
            success=False,
            path=file_path,
            name=os.path.basename(file_path),
            size=0,
            mode="append" if append else "write",
            error=str(e)
        )

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
                                    
                                    file_search_result = FileSearchResult(
                                        **metadata.dict(),
                                        match=FileMatch(
                                            context=content[start:end],
                                            line=line_number
                                        )
                                    )
                                    
                                    results.append(file_search_result)
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
                                    
                                    file_search_result = FileSearchResult(
                                        **metadata.dict(),
                                        match=FileMatch(
                                            context=content[start:end],
                                            line=line_number
                                        )
                                    )
                                    
                                    results.append(file_search_result)
                                    count += 1
                        except Exception:
                            # Skip files that can't be read as text
                            pass
    except Exception as e:
        return {"error": str(e)}
    
    return results

# MCP Tool: Scan Directory
@mcp.tool()
def scan_directory_tool(directory_path: str, recursive: bool = True, file_types: list = None) -> Dict[str, Any]:
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
        return ScanDirectoryResult(
            directory=directory_path,
            file_count=0,
            files=[],
            error=f"Directory not found: {directory_path}"
        ).model_dump()
    
    # Scan the directory
    results = scan_directory(directory_path, recursive, file_types)
    
    if isinstance(results, dict) and "error" in results:
        return ScanDirectoryResult(
            directory=directory_path,
            file_count=0,
            files=[],
            error=results["error"]
        ).model_dump()
    
    return ScanDirectoryResult(
        directory=directory_path,
        file_count=len(results),
        files=results
    ).model_dump()

# MCP Tool: Get File Metadata
@mcp.tool()
def get_file_metadata_tool(file_path: str) -> Dict[str, Any]:
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
        return FileMetadata(
            path=file_path,
            name=os.path.basename(file_path),
            size=0,
            created=datetime.now().isoformat(),
            modified=datetime.now().isoformat(),
            type="unknown",
            error=f"File not found: {file_path}"
        ).model_dump()
    
    # Get the file metadata
    metadata = get_file_metadata(file_path)
    
    return metadata.model_dump()

# MCP Tool: List Drives (Windows-specific)
@mcp.tool()
def list_drives() -> Dict[str, Any]:
    """
    List available drives on Windows.
    
    Returns:
        A list of available drives
    """
    if SYSTEM != "Windows":
        return DriveListing(
            drives=[],
            error="This function is only available on Windows"
        ).model_dump()
    
    try:
        if 'get_windows_drives' in globals():
            return get_windows_drives()
        
        # Use a simpler approach to get drive information
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                # Try to determine drive type by checking if it's a mount point
                drive_type = "Fixed" if os.path.ismount(drive) else "Unknown"
                drives.append(DriveInfo(
                    path=drive,
                    type=drive_type
                ))
        
        return DriveListing(drives=drives).model_dump()
    except Exception as e:
        return DriveListing(
            drives=[],
            error=str(e)
        ).model_dump()

# MCP Tool: Create Collection
@mcp.tool()
def create_collection(name: str, file_paths: list, storage_path: str = None) -> Dict[str, Any]:
    """
    Create a collection of files.
    
    Args:
        name: The name of the collection
        file_paths: List of file paths to include in the collection
        storage_path: Optional path where to store the collection. If not provided, uses default location.
    
    Returns:
        Information about the created collection
    """
    # Use provided storage path or default to collections directory
    collection_dir = os.path.join(storage_path if storage_path else DEFAULT_COLLECTIONS_DIR, name)
    
    try:
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
                collection_info["files"].append(metadata.model_dump())
        
        # Save collection info
        with open(os.path.join(collection_dir, "collection.json"), "w") as f:
            json.dump(collection_info, f, indent=2)
        
        return CollectionResult(
            collection=name,
            file_count=len(collection_info["files"]),
            path=collection_dir
        ).model_dump()
    except Exception as e:
        return CollectionResult(
            collection=name,
            file_count=0,
            path=collection_dir,
            error=str(e)
        ).model_dump()

# MCP Tool: List User Directories
@mcp.tool()
def list_user_directories() -> Dict[str, Any]:
    """
    List common user directories based on the operating system.
    
    Returns:
        A list of common user directories
    """
    directories = {}
    
    try:
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
        
        return UserDirectoriesResult(directories=directories).model_dump()
    except Exception as e:
        return UserDirectoriesResult(
            directories={},
            error=str(e)
        ).model_dump()

# MCP Tool: Read Text File
@mcp.tool()
def read_text_file_tool(file_path: str, max_lines: int = None) -> Dict[str, Any]:
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
    
    return read_text_file(file_path, max_lines).model_dump()

# MCP Tool: Write Text File
@mcp.tool()
def write_text_file_tool(file_path: str, content: str, append: bool = False) -> Dict[str, Any]:
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
    
    return write_text_file(file_path, content, append).model_dump()

# MCP Tool: Search Files
@mcp.tool()
def search_files_tool(directory_path: str, query: str, recursive: bool = True, file_types: list = None) -> Dict[str, Any]:
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
        return SearchFilesResult(
            directory=directory_path,
            query=query,
            match_count=0,
            matches=[],
            error=f"Directory not found: {directory_path}"
        ).model_dump()
    
    # Search the directory
    results = search_files(directory_path, query, recursive, file_types)
    
    if isinstance(results, dict) and "error" in results:
        return SearchFilesResult(
            directory=directory_path,
            query=query,
            match_count=0,
            matches=[],
            error=results["error"]
        ).model_dump()
    
    return SearchFilesResult(
        directory=directory_path,
        query=query,
        match_count=len(results),
        matches=results
    ).model_dump()

# MCP Tool: Search File Contents
@mcp.tool()
def search_file_contents_tool(directory_path: str, query: str, recursive: bool = True, file_types: list = None, max_results: int = 100) -> Dict[str, Any]:
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
        return SearchFileContentsResult(
            directory=directory_path,
            query=query,
            match_count=0,
            matches=[],
            error=f"Directory not found: {directory_path}"
        ).model_dump()
    
    # Search the directory
    results = search_file_contents(directory_path, query, recursive, file_types, max_results)
    
    if isinstance(results, dict) and "error" in results:
        return SearchFileContentsResult(
            directory=directory_path,
            query=query,
            match_count=0,
            matches=[],
            error=results["error"]
        ).model_dump()
    
    return SearchFileContentsResult(
        directory=directory_path,
        query=query,
        match_count=len(results),
        matches=results
    ).model_dump()

# MCP Tool: Get System Information
@mcp.tool()
def get_system_info() -> Dict[str, Any]:
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
        
        return SystemInfoResult(system_info=SystemInfo(**info)).model_dump()
    except Exception as e:
        return SystemInfoResult(
            system_info=SystemInfo(
                system=platform.system(),
                node="unknown",
                release="unknown",
                version="unknown",
                machine="unknown",
                processor="unknown",
                python_version=platform.python_version(),
                user_home=os.path.expanduser("~")
            ),
            error=str(e)
        ).model_dump()

# MCP Tool: Copy File
@mcp.tool()
def copy_file(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
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
            return FileCopyResult(
                success=False,
                source=source_path,
                destination=destination_path,
                size=0,
                error=f"Source file not found: {source_path}"
            ).model_dump()
        
        # Check if the destination file exists
        if os.path.exists(destination_path) and not overwrite:
            return FileCopyResult(
                success=False,
                source=source_path,
                destination=destination_path,
                size=0,
                error=f"Destination file already exists: {destination_path}"
            ).model_dump()
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        
        # Copy the file
        shutil.copy2(source_path, destination_path)
        
        return FileCopyResult(
            success=True,
            source=source_path,
            destination=destination_path,
            size=os.path.getsize(destination_path)
        ).model_dump()
    except Exception as e:
        return FileCopyResult(
            success=False,
            source=source_path,
            destination=destination_path,
            size=0,
            error=str(e)
        ).model_dump()

# MCP Tool: Move File
@mcp.tool()
def move_file(source_path: str, destination_path: str, overwrite: bool = False) -> Dict[str, Any]:
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
            return FileMoveResult(
                success=False,
                source=source_path,
                destination=destination_path,
                size=0,
                error=f"Source file not found: {source_path}"
            ).model_dump()
        
        # Check if the destination file exists
        if os.path.exists(destination_path) and not overwrite:
            return FileMoveResult(
                success=False,
                source=source_path,
                destination=destination_path,
                size=0,
                error=f"Destination file already exists: {destination_path}"
            ).model_dump()
        
        # Create destination directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        
        # Get file size before moving
        file_size = os.path.getsize(source_path)
        
        # Move the file
        shutil.move(source_path, destination_path)
        
        return FileMoveResult(
            success=True,
            source=source_path,
            destination=destination_path,
            size=file_size
        ).model_dump()
    except Exception as e:
        return FileMoveResult(
            success=False,
            source=source_path,
            destination=destination_path,
            size=0,
            error=str(e)
        ).model_dump()

# MCP Tool: Delete File
@mcp.tool()
def delete_file(file_path: str) -> Dict[str, Any]:
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
            return FileDeleteResult(
                success=False,
                deleted_file=FileDeleteInfo(
                    path=file_path,
                    name=os.path.basename(file_path),
                    size=0
                ),
                error=f"File not found: {file_path}"
            ).model_dump()
        
        # Get file info before deletion
        file_info = FileDeleteInfo(
            path=file_path,
            name=os.path.basename(file_path),
            size=os.path.getsize(file_path)
        )
        
        # Delete the file
        os.remove(file_path)
        
        return FileDeleteResult(
            success=True,
            deleted_file=file_info
        ).model_dump()
    except Exception as e:
        return FileDeleteResult(
            success=False,
            deleted_file=FileDeleteInfo(
                path=file_path,
                name=os.path.basename(file_path),
                size=0
            ),
            error=str(e)
        ).model_dump()

# MCP Tool: Create Directory
@mcp.tool()
def create_directory(directory_path: str) -> Dict[str, Any]:
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
        
        return DirectoryCreateResult(
            success=True,
            path=directory_path
        ).model_dump()
    except Exception as e:
        return DirectoryCreateResult(
            success=False,
            path=directory_path,
            error=str(e)
        ).model_dump()

# MCP Tool: List Directory
@mcp.tool()
def list_directory(directory_path: str) -> Dict[str, Any]:
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
            return DirectoryListing(
                path=directory_path,
                files=[],
                directories=[],
                file_count=0,
                directory_count=0,
                error=f"Directory not found: {directory_path}"
            ).model_dump()
        
        # List the directory contents
        items = os.listdir(directory_path)
        
        files = []
        directories = []
        
        for item in items:
            item_path = os.path.join(directory_path, item)
            
            if os.path.isfile(item_path):
                files.append(FileItem(
                    name=item,
                    path=item_path,
                    size=os.path.getsize(item_path),
                    type=get_file_type(item_path)
                ))
            elif os.path.isdir(item_path):
                directories.append(DirectoryItem(
                    name=item,
                    path=item_path
                ))
        
        return DirectoryListing(
            path=directory_path,
            files=files,
            directories=directories,
            file_count=len(files),
            directory_count=len(directories)
        ).model_dump()
    except Exception as e:
        return DirectoryListing(
            path=directory_path,
            files=[],
            directories=[],
            file_count=0,
            directory_count=0,
            error=str(e)
        ).model_dump()

# MCP Tool: List Directory Recursively
@mcp.tool()
def list_directory_recursively(directory_path: str, max_depth: int = 3) -> Dict[str, Any]:
    """
    List the contents of a directory recursively, showing the directory structure.
    
    Args:
        directory_path: The path to the directory to list
        max_depth: Maximum depth of recursion (default: 3)
    
    Returns:
        A string representation of the directory structure
    """
    try:
        # Validate and normalize the path
        if SYSTEM == "Windows":
            directory_path = os.path.normpath(directory_path)
        
        # Check if the directory exists
        if not os.path.isdir(directory_path):
            return RecursiveDirectoryListing(
                path=directory_path,
                structure="",
                file_count=0,
                directory_count=0,
                error=f"Directory not found: {directory_path}"
            ).model_dump()
        
        def build_tree(path: str, prefix: str = "", depth: int = 0) -> tuple[str, int, int]:
            if depth >= max_depth:
                return "", 0, 0
            
            tree = []
            file_count = 0
            dir_count = 0
            
            try:
                items = os.listdir(path)
                items.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    item_path = os.path.join(path, item)
                    
                    # Add the current item to the tree
                    tree.append(f"{prefix}{'└── ' if is_last else '├── '}{item}")
                    
                    if os.path.isdir(item_path):
                        dir_count += 1
                        # Recursively process subdirectories
                        sub_tree, sub_files, sub_dirs = build_tree(
                            item_path,
                            prefix + ('    ' if is_last else '│   '),
                            depth + 1
                        )
                        tree.append(sub_tree)
                        file_count += sub_files
                        dir_count += sub_dirs
                    else:
                        file_count += 1
                
                return '\n'.join(tree), file_count, dir_count
            except Exception as e:
                return f"Error reading directory: {str(e)}", 0, 0
        
        # Build the tree structure
        tree_structure, file_count, dir_count = build_tree(directory_path)
        
        return RecursiveDirectoryListing(
            path=directory_path,
            structure=tree_structure,
            file_count=file_count,
            directory_count=dir_count
        ).model_dump()
    except Exception as e:
        return RecursiveDirectoryListing(
            path=directory_path,
            structure="",
            file_count=0,
            directory_count=0,
            error=str(e)
        ).model_dump()

# Start the MCP server
if __name__ == "__main__":
    print(f"File System MCP Server starting...")
    print(f"Operating System: {SYSTEM}")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Default Collections Directory: {DEFAULT_COLLECTIONS_DIR}")
    mcp.run()
