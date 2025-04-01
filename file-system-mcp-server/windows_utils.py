# Windows-specific utilities for Local Media MCP Server
import os
import platform
import json
from datetime import datetime

# Check if we're running on Windows
def is_windows():
    return platform.system() == "Windows"

# Get Windows drives with PyWin32
def get_windows_drives():
    """
    Get a list of available drives on Windows using PyWin32.
    Returns a list of drive information dictionaries.
    """
    if not is_windows():
        return {"error": "This function is only available on Windows"}
    
    try:
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
                
                # Try to get drive information
                try:
                    free_bytes, total_bytes, total_free_bytes = win32api.GetDiskFreeSpaceEx(drive)
                    size_info = {
                        "total_bytes": total_bytes,
                        "free_bytes": free_bytes,
                        "used_bytes": total_bytes - free_bytes,
                        "percent_used": round((total_bytes - free_bytes) / total_bytes * 100, 2) if total_bytes > 0 else 0
                    }
                except:
                    size_info = {"error": "Could not retrieve size information"}
                
                # Try to get volume information
                try:
                    volume_name, volume_serial, max_component_length, fs_flags, fs_name = win32api.GetVolumeInformation(drive)
                    volume_info = {
                        "name": volume_name,
                        "filesystem": fs_name
                    }
                except:
                    volume_info = {"error": "Could not retrieve volume information"}
                
                drive_info.append({
                    "path": drive,
                    "type": type_name,
                    "size": size_info,
                    "volume": volume_info
                })
            except Exception as e:
                drive_info.append({
                    "path": drive,
                    "type": "Unknown",
                    "error": str(e)
                })
        
        return {"drives": drive_info}
    except ImportError:
        return {"error": "win32api module not available. Install pywin32 package."}
    except Exception as e:
        return {"error": str(e)}

# Get Windows special folders
def get_windows_special_folders():
    """
    Get a list of Windows special folders using PyWin32.
    Returns a dictionary of special folder paths.
    """
    if not is_windows():
        return {"error": "This function is only available on Windows"}
    
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        
        # Common special folders
        special_folders = {
            "Desktop": "Desktop",
            "Favorites": "Favorites",
            "MyDocuments": "My Documents",
            "Personal": "Personal",
            "Programs": "Programs",
            "Recent": "Recent",
            "SendTo": "SendTo",
            "StartMenu": "Start Menu",
            "Startup": "Startup",
            "Templates": "Templates"
        }
        
        result = {}
        for key, name in special_folders.items():
            try:
                path = shell.SpecialFolders(key)
                if path and os.path.exists(path):
                    result[name] = path
            except:
                pass
        
        # Add additional common folders that might not be in SpecialFolders
        user_profile = os.environ.get("USERPROFILE", "")
        if user_profile:
            for folder in ["Pictures", "Videos", "Music", "Downloads", "3D Objects"]:
                path = os.path.join(user_profile, folder)
                if os.path.exists(path):
                    result[folder] = path
        
        return {"special_folders": result}
    except ImportError:
        return {"error": "win32com module not available. Install pywin32 package."}
    except Exception as e:
        return {"error": str(e)}

# Get Windows environment variables
def get_windows_environment():
    """
    Get Windows environment variables.
    Returns a dictionary of environment variables.
    """
    if not is_windows():
        return {"error": "This function is only available on Windows"}
    
    try:
        # Get common environment variables
        env_vars = {
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "APPDATA": os.environ.get("APPDATA", ""),
            "LOCALAPPDATA": os.environ.get("LOCALAPPDATA", ""),
            "TEMP": os.environ.get("TEMP", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
            "PROGRAMFILES": os.environ.get("PROGRAMFILES", ""),
            "PROGRAMFILES(X86)": os.environ.get("PROGRAMFILES(X86)", ""),
            "PROGRAMDATA": os.environ.get("PROGRAMDATA", ""),
            "WINDIR": os.environ.get("WINDIR", ""),
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")
        }
        
        return {"environment": env_vars}
    except Exception as e:
        return {"error": str(e)}

# Get Windows system information
def get_windows_system_info():
    """
    Get Windows system information.
    Returns a dictionary of system information.
    """
    if not is_windows():
        return {"error": "This function is only available on Windows"}
    
    try:
        import platform
        import socket
        
        # Basic system information
        system_info = {
            "os": platform.system(),
            "version": platform.version(),
            "release": platform.release(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "username": os.environ.get("USERNAME", "")
        }
        
        # Try to get more detailed Windows information
        try:
            import wmi
            c = wmi.WMI()
            
            # OS information
            for os in c.Win32_OperatingSystem():
                system_info["os_name"] = os.Caption
                system_info["os_version"] = os.Version
                system_info["os_build"] = os.BuildNumber
                system_info["os_architecture"] = os.OSArchitecture
                system_info["last_boot"] = os.LastBootUpTime
                system_info["install_date"] = os.InstallDate
                system_info["system_directory"] = os.SystemDirectory
                system_info["windows_directory"] = os.WindowsDirectory
                break
            
            # Computer system information
            for system in c.Win32_ComputerSystem():
                system_info["manufacturer"] = system.Manufacturer
                system_info["model"] = system.Model
                system_info["system_type"] = system.SystemType
                system_info["total_physical_memory"] = system.TotalPhysicalMemory
                break
            
            # Processor information
            processors = []
            for processor in c.Win32_Processor():
                processors.append({
                    "name": processor.Name,
                    "description": processor.Description,
                    "cores": processor.NumberOfCores,
                    "logical_processors": processor.NumberOfLogicalProcessors,
                    "max_clock_speed": processor.MaxClockSpeed
                })
            system_info["processors"] = processors
        except ImportError:
            system_info["wmi_info"] = "WMI module not available. Install wmi package for more detailed information."
        except Exception as e:
            system_info["wmi_error"] = str(e)
        
        return {"system_info": system_info}
    except Exception as e:
        return {"error": str(e)}

# Handle Windows file paths
def normalize_windows_path(path):
    """
    Normalize a Windows file path.
    Handles both forward and backslashes.
    """
    if not path:
        return path
    
    # Replace forward slashes with backslashes
    path = path.replace('/', '\\')
    
    # Normalize the path
    return os.path.normpath(path)

# Check if a path is a valid Windows path
def is_valid_windows_path(path):
    """
    Check if a path is a valid Windows path.
    """
    if not path:
        return False
    
    # Check for invalid characters in Windows paths
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in path:
            return False
    
    # Check for reserved names
    parts = path.split('\\')
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    for part in parts:
        if part.upper() in reserved_names:
            return False
    
    return True


print(get_windows_environment())