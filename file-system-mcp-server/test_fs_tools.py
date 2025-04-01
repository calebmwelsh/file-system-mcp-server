"""
Test script for File System MCP Server tools.
This script tests each of the MCP tools provided by the server.
"""

import json
import os
import platform
import shutil
import sys
import tempfile
from datetime import datetime

# Determine the operating system
SYSTEM = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'

# Create a temporary directory for testing
TEST_DIR = tempfile.mkdtemp(prefix="fs_mcp_test_")
print(f"Created temporary test directory: {TEST_DIR}")

# Create test files
def create_test_files():
    """Create test files for testing the MCP tools."""
    # Create a text file
    text_file_path = os.path.join(TEST_DIR, "test.txt")
    with open(text_file_path, "w") as f:
        f.write("This is a test file.\nIt has multiple lines.\nThis is line 3.")
    
    # Create a JSON file
    json_file_path = os.path.join(TEST_DIR, "test.json")
    with open(json_file_path, "w") as f:
        json.dump({"name": "Test", "value": 123, "items": ["a", "b", "c"]}, f, indent=2)
    
    # Create a Python file
    py_file_path = os.path.join(TEST_DIR, "test.py")
    with open(py_file_path, "w") as f:
        f.write("""#!/usr/bin/env python3
def hello():
    print("Hello, world!")

if __name__ == "__main__":
    hello()
""")
    
    # Create a subdirectory
    subdir_path = os.path.join(TEST_DIR, "subdir")
    os.makedirs(subdir_path, exist_ok=True)
    
    # Create a file in the subdirectory
    subdir_file_path = os.path.join(subdir_path, "subdir_file.txt")
    with open(subdir_file_path, "w") as f:
        f.write("This is a file in a subdirectory.")
    
    print("Created test files:")
    print(f"- {text_file_path}")
    print(f"- {json_file_path}")
    print(f"- {py_file_path}")
    print(f"- {subdir_path}")
    print(f"- {subdir_file_path}")
    
    return {
        "text_file": text_file_path,
        "json_file": json_file_path,
        "py_file": py_file_path,
        "subdir": subdir_path,
        "subdir_file": subdir_file_path
    }

# Clean up test files
def cleanup():
    """Clean up the temporary test directory."""
    try:
        shutil.rmtree(TEST_DIR)
        print(f"Cleaned up temporary test directory: {TEST_DIR}")
    except Exception as e:
        print(f"Error cleaning up: {e}")

# Test functions for each MCP tool
def test_scan_directory_tool():
    """Test the scan_directory_tool."""
    print("\n=== Testing scan_directory_tool ===")
    
    # Import the function from the server module
    try:
        from fs_server import scan_directory_tool

        # Test with recursive=True
        print("Testing with recursive=True:")
        result = scan_directory_tool(TEST_DIR, True)
        print(f"Found {result.get('file_count', 0)} files")
        
        # Test with recursive=False
        print("Testing with recursive=False:")
        result = scan_directory_tool(TEST_DIR, False)
        print(f"Found {result.get('file_count', 0)} files")
        
        # Test with specific file types
        print("Testing with specific file types:")
        result = scan_directory_tool(TEST_DIR, True, ["text"])
        print(f"Found {result.get('file_count', 0)} text files")
        
        print("scan_directory_tool test: SUCCESS")
        return True
    except Exception as e:
        print(f"scan_directory_tool test: FAILED - {e}")
        return False

def test_get_file_metadata_tool():
    """Test the get_file_metadata_tool."""
    print("\n=== Testing get_file_metadata_tool ===")
    
    # Import the function from the server module
    try:
        from fs_server import get_file_metadata_tool

        # Test with a text file
        print("Testing with a text file:")
        result = get_file_metadata_tool(os.path.join(TEST_DIR, "test.txt"))
        print(f"File type: {result.get('type', 'unknown')}")
        print(f"File size: {result.get('size', 0)} bytes")
        
        # Test with a JSON file
        print("Testing with a JSON file:")
        result = get_file_metadata_tool(os.path.join(TEST_DIR, "test.json"))
        print(f"File type: {result.get('type', 'unknown')}")
        print(f"File size: {result.get('size', 0)} bytes")
        
        # Test with a Python file
        print("Testing with a Python file:")
        result = get_file_metadata_tool(os.path.join(TEST_DIR, "test.py"))
        print(f"File type: {result.get('type', 'unknown')}")
        print(f"File size: {result.get('size', 0)} bytes")
        
        print("get_file_metadata_tool test: SUCCESS")
        return True
    except Exception as e:
        print(f"get_file_metadata_tool test: FAILED - {e}")
        return False

def test_list_drives():
    """Test the list_drives tool."""
    print("\n=== Testing list_drives ===")
    
    # Import the function from the server module
    try:
        from fs_server import list_drives

        # This function is Windows-specific
        if SYSTEM == "Windows":
            print("Testing list_drives on Windows:")
            result = list_drives()
            if "drives" in result:
                print(f"Found {len(result['drives'])} drives")
                for drive in result["drives"]:
                    print(f"- {drive.get('path', 'unknown')}: {drive.get('type', 'unknown')}")
                print("list_drives test: SUCCESS")
                return True
            else:
                print(f"list_drives test: FAILED - {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"Skipping list_drives test on {SYSTEM}")
            return True
    except Exception as e:
        print(f"list_drives test: FAILED - {e}")
        return False

def test_list_user_directories():
    """Test the list_user_directories tool."""
    print("\n=== Testing list_user_directories ===")
    
    # Import the function from the server module
    try:
        from fs_server import list_user_directories
        
        print("Testing list_user_directories:")
        result = list_user_directories()
        if "directories" in result:
            print(f"Found {len(result['directories'])} directories")
            for name, path in result["directories"].items():
                print(f"- {name}: {path}")
            print("list_user_directories test: SUCCESS")
            return True
        else:
            print(f"list_user_directories test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"list_user_directories test: FAILED - {e}")
        return False

def test_read_text_file_tool():
    """Test the read_text_file_tool."""
    print("\n=== Testing read_text_file_tool ===")
    
    # Import the function from the server module
    try:
        from fs_server import read_text_file_tool

        # Test reading a text file
        print("Testing reading a text file:")
        result = read_text_file_tool(os.path.join(TEST_DIR, "test.txt"))
        if "content" in result:
            print(f"Content: {result['content']}")
            
            # Test with max_lines
            print("Testing with max_lines=1:")
            result = read_text_file_tool(os.path.join(TEST_DIR, "test.txt"), 1)
            print(f"Content: {result['content']}")
            
            print("read_text_file_tool test: SUCCESS")
            return True
        else:
            print(f"read_text_file_tool test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"read_text_file_tool test: FAILED - {e}")
        return False

def test_write_text_file_tool():
    """Test the write_text_file_tool."""
    print("\n=== Testing write_text_file_tool ===")
    
    # Import the function from the server module
    try:
        from fs_server import write_text_file_tool

        # Test writing a new file
        new_file_path = os.path.join(TEST_DIR, "new_file.txt")
        print(f"Testing writing a new file: {new_file_path}")
        result = write_text_file_tool(new_file_path, "This is a new file created by the test script.")
        if result.get("success", False):
            print(f"Successfully wrote file: {result.get('path')}")
            
            # Test appending to the file
            print("Testing appending to the file:")
            result = write_text_file_tool(new_file_path, "\nThis line was appended.", True)
            if result.get("success", False):
                print(f"Successfully appended to file: {result.get('path')}")
                
                # Verify the content
                with open(new_file_path, "r") as f:
                    content = f.read()
                    print(f"File content: {content}")
                
                print("write_text_file_tool test: SUCCESS")
                return True
            else:
                print(f"write_text_file_tool append test: FAILED - {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"write_text_file_tool test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"write_text_file_tool test: FAILED - {e}")
        return False

def test_search_files_tool():
    """Test the search_files_tool."""
    print("\n=== Testing search_files_tool ===")
    
    # Import the function from the server module
    try:
        from fs_server import search_files_tool

        # Test searching for files
        print("Testing searching for files with 'test' in the name:")
        result = search_files_tool(TEST_DIR, "test", True)
        if "matches" in result:
            print(f"Found {result.get('match_count', 0)} matches")
            for match in result["matches"]:
                print(f"- {match.get('path', 'unknown')}")
            
            # Test with specific file types
            print("Testing with specific file types:")
            result = search_files_tool(TEST_DIR, "test", True, ["text"])
            print(f"Found {result.get('match_count', 0)} text files")
            
            print("search_files_tool test: SUCCESS")
            return True
        else:
            print(f"search_files_tool test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"search_files_tool test: FAILED - {e}")
        return False

def test_search_file_contents_tool():
    """Test the search_file_contents_tool."""
    print("\n=== Testing search_file_contents_tool ===")
    
    # Import the function from the server module
    try:
        from fs_server import search_file_contents_tool

        # Test searching for file contents
        print("Testing searching for 'line' in file contents:")
        result = search_file_contents_tool(TEST_DIR, "line", True)
        if "matches" in result:
            print(f"Found {result.get('match_count', 0)} matches")
            for match in result["matches"]:
                print(f"- {match.get('path', 'unknown')}")
                if "match" in match:
                    print(f"  Line: {match['match'].get('line', 'unknown')}")
                    print(f"  Context: {match['match'].get('context', 'unknown')}")
            
            print("search_file_contents_tool test: SUCCESS")
            return True
        else:
            print(f"search_file_contents_tool test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"search_file_contents_tool test: FAILED - {e}")
        return False

def test_get_system_info():
    """Test the get_system_info tool."""
    print("\n=== Testing get_system_info ===")
    
    # Import the function from the server module
    try:
        from fs_server import get_system_info
        
        print("Testing get_system_info:")
        result = get_system_info()
        if "system_info" in result:
            system_info = result["system_info"]
            print(f"System: {system_info.get('system', 'unknown')}")
            print(f"Node: {system_info.get('node', 'unknown')}")
            print(f"Release: {system_info.get('release', 'unknown')}")
            print(f"Version: {system_info.get('version', 'unknown')}")
            print(f"Machine: {system_info.get('machine', 'unknown')}")
            print(f"Processor: {system_info.get('processor', 'unknown')}")
            print(f"Python Version: {system_info.get('python_version', 'unknown')}")
            
            print("get_system_info test: SUCCESS")
            return True
        else:
            print(f"get_system_info test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"get_system_info test: FAILED - {e}")
        return False

def test_copy_file():
    """Test the copy_file tool."""
    print("\n=== Testing copy_file ===")
    
    # Import the function from the server module
    try:
        from fs_server import copy_file

        # Test copying a file
        source_path = os.path.join(TEST_DIR, "test.txt")
        dest_path = os.path.join(TEST_DIR, "test_copy.txt")
        print(f"Testing copying {source_path} to {dest_path}:")
        result = copy_file(source_path, dest_path)
        if result.get("success", False):
            print(f"Successfully copied file: {result.get('destination')}")
            
            # Verify the file exists
            if os.path.isfile(dest_path):
                print(f"Verified file exists: {dest_path}")
                
                # Test overwrite=False (should fail)
                print("Testing with overwrite=False (should fail):")
                result = copy_file(source_path, dest_path, False)
                if "error" in result:
                    print(f"Expected error: {result['error']}")
                    
                    # Test overwrite=True
                    print("Testing with overwrite=True:")
                    result = copy_file(source_path, dest_path, True)
                    if result.get("success", False):
                        print(f"Successfully overwrote file: {result.get('destination')}")
                        print("copy_file test: SUCCESS")
                        return True
                    else:
                        print(f"copy_file overwrite test: FAILED - {result.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"copy_file overwrite=False test: FAILED - Expected an error")
                    return False
            else:
                print(f"copy_file test: FAILED - Destination file does not exist")
                return False
        else:
            print(f"copy_file test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"copy_file test: FAILED - {e}")
        return False

def test_move_file():
    """Test the move_file tool."""
    print("\n=== Testing move_file ===")
    
    # Import the function from the server module
    try:
        from fs_server import move_file

        # Create a file to move
        source_path = os.path.join(TEST_DIR, "move_source.txt")
        with open(source_path, "w") as f:
            f.write("This file will be moved.")
        
        # Test moving a file
        dest_path = os.path.join(TEST_DIR, "move_dest.txt")
        print(f"Testing moving {source_path} to {dest_path}:")
        result = move_file(source_path, dest_path)
        if result.get("success", False):
            print(f"Successfully moved file: {result.get('destination')}")
            
            # Verify the source file no longer exists
            if not os.path.isfile(source_path):
                print(f"Verified source file no longer exists: {source_path}")
                
                # Verify the destination file exists
                if os.path.isfile(dest_path):
                    print(f"Verified destination file exists: {dest_path}")
                    print("move_file test: SUCCESS")
                    return True
                else:
                    print(f"move_file test: FAILED - Destination file does not exist")
                    return False
            else:
                print(f"move_file test: FAILED - Source file still exists")
                return False
        else:
            print(f"move_file test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"move_file test: FAILED - {e}")
        return False

def test_delete_file():
    """Test the delete_file tool."""
    print("\n=== Testing delete_file ===")
    
    # Import the function from the server module
    try:
        from fs_server import delete_file

        # Create a file to delete
        file_path = os.path.join(TEST_DIR, "delete_me.txt")
        with open(file_path, "w") as f:
            f.write("This file will be deleted.")
        
        # Test deleting a file
        print(f"Testing deleting {file_path}:")
        result = delete_file(file_path)
        if result.get("success", False):
            print(f"Successfully deleted file: {result.get('deleted_file', {}).get('path')}")
            
            # Verify the file no longer exists
            if not os.path.isfile(file_path):
                print(f"Verified file no longer exists: {file_path}")
                print("delete_file test: SUCCESS")
                return True
            else:
                print(f"delete_file test: FAILED - File still exists")
                return False
        else:
            print(f"delete_file test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"delete_file test: FAILED - {e}")
        return False

def test_create_directory():
    """Test the create_directory tool."""
    print("\n=== Testing create_directory ===")
    
    # Import the function from the server module
    try:
        from fs_server import create_directory

        # Test creating a directory
        dir_path = os.path.join(TEST_DIR, "new_directory")
        print(f"Testing creating directory {dir_path}:")
        result = create_directory(dir_path)
        if result.get("success", False):
            print(f"Successfully created directory: {result.get('path')}")
            
            # Verify the directory exists
            if os.path.isdir(dir_path):
                print(f"Verified directory exists: {dir_path}")
                
                # Test creating the same directory again (should succeed with exist_ok=True)
                print("Testing creating the same directory again:")
                result = create_directory(dir_path)
                if result.get("success", False):
                    print(f"Successfully created directory (already existed): {result.get('path')}")
                    print("create_directory test: SUCCESS")
                    return True
                else:
                    print(f"create_directory test: FAILED - {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"create_directory test: FAILED - Directory does not exist")
                return False
        else:
            print(f"create_directory test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"create_directory test: FAILED - {e}")
        return False

def test_list_directory():
    """Test the list_directory tool."""
    print("\n=== Testing list_directory ===")
    
    # Import the function from the server module
    try:
        from fs_server import list_directory

        # Test listing a directory
        print(f"Testing listing directory {TEST_DIR}:")
        result = list_directory(TEST_DIR)
        if "files" in result and "directories" in result:
            print(f"Found {result.get('file_count', 0)} files and {result.get('directory_count', 0)} directories")
            
            print("Files:")
            for file in result["files"]:
                print(f"- {file.get('name', 'unknown')} ({file.get('type', 'unknown')})")
            
            print("Directories:")
            for directory in result["directories"]:
                print(f"- {directory.get('name', 'unknown')}")
            
            print("list_directory test: SUCCESS")
            return True
        else:
            print(f"list_directory test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"list_directory test: FAILED - {e}")
        return False

def test_create_collection():
    """Test the create_collection tool."""
    print("\n=== Testing create_collection ===")
    
    # Import the function from the server module
    try:
        from fs_server import create_collection

        # Test creating a collection
        collection_name = "test_collection"
        file_paths = [
            os.path.join(TEST_DIR, "test.txt"),
            os.path.join(TEST_DIR, "test.json"),
            os.path.join(TEST_DIR, "test.py")
        ]
        print(f"Testing creating collection {collection_name} with {len(file_paths)} files:")
        result = create_collection(collection_name, file_paths)
        if "collection" in result:
            print(f"Created collection: {result.get('collection')}")
            print(f"File count: {result.get('file_count', 0)}")
            print(f"Path: {result.get('path')}")
            
            # Verify the collection file exists
            collection_file = os.path.join(result.get('path'), "collection.json")
            if os.path.isfile(collection_file):
                print(f"Verified collection file exists: {collection_file}")
                
                # Read the collection file
                with open(collection_file, "r") as f:
                    collection_data = json.load(f)
                    print(f"Collection name: {collection_data.get('name')}")
                    print(f"File count: {len(collection_data.get('files', []))}")
                
                print("create_collection test: SUCCESS")
                return True
            else:
                print(f"create_collection test: FAILED - Collection file does not exist")
                return False
        else:
            print(f"create_collection test: FAILED - {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"create_collection test: FAILED - {e}")
        return False

def run_all_tests():
    """Run all tests."""
    print("=== Running all tests ===")
    
    # Create test files
    test_files = create_test_files()
    
    # Run tests
    tests = [
        test_scan_directory_tool,
        test_get_file_metadata_tool,
        test_list_drives,
        test_list_user_directories,
        test_read_text_file_tool,
        test_write_text_file_tool,
        test_search_files_tool,
        test_search_file_contents_tool,
        test_get_system_info,
        test_copy_file,
        test_move_file,
        test_delete_file,
        test_create_directory,
        test_list_directory,
        test_create_collection
    ]
    
    results = {}
    for test_func in tests:
        test_name = test_func.__name__
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"{test_name}: FAILED - Unexpected error: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n=== Test Summary ===")
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    print(f"Passed: {success_count}/{total_count} tests ({success_count/total_count*100:.1f}%)")
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
    
    # Clean up
    cleanup()
    
    return success_count == total_count

if __name__ == "__main__":
    # Add the parent directory to the path so we can import the server module
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Run all tests
    success = run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
