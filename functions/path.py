import os
import winreg
import ctypes

# ANSI escape codes for CLI colors
RESET = "\033[0m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_RED = "\033[91m"


def add_to_path(directory, scope='system'):
    """
    Add a directory to the PATH environment variable.
    
    Args:
        directory (str): The directory path to add to PATH
        scope (str): Either 'system' or 'user' to specify which PATH to modify
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Normalize the directory path
        directory = os.path.abspath(directory)
        
        if scope == 'system':
            key_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
            hkey = winreg.HKEY_LOCAL_MACHINE
        elif scope == 'user':
            key_path = r'Environment'
            hkey = winreg.HKEY_CURRENT_USER
        else:
            print(f"{BRIGHT_RED}Invalid scope '{scope}'. Use 'system' or 'user'.{RESET}")
            return False
        
        # Open the Environment registry key
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
        
        # Read current PATH
        current_path, reg_type = winreg.QueryValueEx(key, 'Path')
        
        # Split PATH into individual directories
        path_dirs = [p.strip() for p in current_path.split(';') if p.strip()]
        
        # Check if directory is already in PATH (case-insensitive)
        directory_lower = directory.lower()
        if any(p.lower() == directory_lower for p in path_dirs):
            print(f"{BRIGHT_YELLOW}'{directory}' is already in {scope} PATH.{RESET}")
            winreg.CloseKey(key)
            return True
        
        # Add directory to PATH
        path_dirs.append(directory)
        new_path = ';'.join(path_dirs)
        
        winreg.SetValueEx(key, 'Path', 0, reg_type, new_path)
        winreg.CloseKey(key)
        
        print(f"{BRIGHT_GREEN}Added '{directory}' to {scope} PATH.{RESET}")
        
        # Broadcast WM_SETTINGCHANGE to notify other programs
        _broadcast_environment_change()
        
        return True
        
    except PermissionError:
        print(f"{BRIGHT_RED}Permission denied. Administrator privileges required for system PATH.{RESET}")
        return False
    except Exception as e:
        print(f"{BRIGHT_RED}Failed to add to PATH: {e}{RESET}")
        return False


def remove_from_path(directory, scope='system'):
    """
    Remove a directory from the PATH environment variable.
    
    Args:
        directory (str): The directory path to remove from PATH
        scope (str): Either 'system' or 'user' to specify which PATH to modify
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Normalize the directory path
        directory = os.path.abspath(directory)
        
        if scope == 'system':
            key_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
            hkey = winreg.HKEY_LOCAL_MACHINE
        elif scope == 'user':
            key_path = r'Environment'
            hkey = winreg.HKEY_CURRENT_USER
        else:
            print(f"{BRIGHT_RED}Invalid scope '{scope}'. Use 'system' or 'user'.{RESET}")
            return False
        
        # Open the Environment registry key
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
        
        # Read current PATH
        current_path, reg_type = winreg.QueryValueEx(key, 'Path')
        
        # Split PATH into individual directories
        path_dirs = [p.strip() for p in current_path.split(';') if p.strip()]
        
        # Remove matching directories (case-insensitive)
        directory_lower = directory.lower()
        original_count = len(path_dirs)
        path_dirs = [p for p in path_dirs if p.lower() != directory_lower]
        
        if len(path_dirs) == original_count:
            print(f"{BRIGHT_YELLOW}'{directory}' was not found in {scope} PATH.{RESET}")
            winreg.CloseKey(key)
            return True
        
        # Update PATH
        new_path = ';'.join(path_dirs)
        winreg.SetValueEx(key, 'Path', 0, reg_type, new_path)
        winreg.CloseKey(key)
        
        print(f"{BRIGHT_GREEN}Removed '{directory}' from {scope} PATH.{RESET}")
        
        # Broadcast WM_SETTINGCHANGE to notify other programs
        _broadcast_environment_change()
        
        return True
        
    except PermissionError:
        print(f"{BRIGHT_RED}Permission denied. Administrator privileges required for system PATH.{RESET}")
        return False
    except Exception as e:
        print(f"{BRIGHT_RED}Failed to remove from PATH: {e}{RESET}")
        return False


def get_path(scope='system'):
    """
    Get the current PATH environment variable.
    
    Args:
        scope (str): Either 'system' or 'user' to specify which PATH to retrieve
    
    Returns:
        list: List of directories in PATH, or None if failed
    """
    try:
        if scope == 'system':
            key_path = r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
            hkey = winreg.HKEY_LOCAL_MACHINE
        elif scope == 'user':
            key_path = r'Environment'
            hkey = winreg.HKEY_CURRENT_USER
        else:
            print(f"{BRIGHT_RED}Invalid scope '{scope}'. Use 'system' or 'user'.{RESET}")
            return None
        
        key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
        current_path, _ = winreg.QueryValueEx(key, 'Path')
        winreg.CloseKey(key)
        
        return [p.strip() for p in current_path.split(';') if p.strip()]
        
    except Exception as e:
        print(f"{BRIGHT_RED}Failed to read PATH: {e}{RESET}")
        return None


def is_in_path(directory, scope='system'):
    """
    Check if a directory is in the PATH environment variable.
    
    Args:
        directory (str): The directory path to check
        scope (str): Either 'system' or 'user' to specify which PATH to check
    
    Returns:
        bool: True if directory is in PATH, False otherwise
    """
    path_dirs = get_path(scope)
    if path_dirs is None:
        return False
    
    directory = os.path.abspath(directory).lower()
    return any(p.lower() == directory for p in path_dirs)


def _broadcast_environment_change():
    """Broadcast WM_SETTINGCHANGE message to notify other programs of environment changes."""
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.c_long()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            ctypes.byref(result)
        )
    except Exception:
        # Silently fail - not critical if broadcast doesn't work
        pass
