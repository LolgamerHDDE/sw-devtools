import os
import sys
import subprocess
import urllib.request
import json
import zipfile
import ctypes
import winreg
import shutil
from .admin import is_admin, request_admin_privileges
from .path import add_to_path

# ANSI escape codes for CLI colors
RESET = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Text Colors
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright Text Colors
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background Colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

# Bright Background Colors
BG_BRIGHT_BLACK = "\033[100m"
BG_BRIGHT_RED = "\033[101m"
BG_BRIGHT_GREEN = "\033[102m"
BG_BRIGHT_YELLOW = "\033[103m"
BG_BRIGHT_BLUE = "\033[104m"
BG_BRIGHT_MAGENTA = "\033[105m"
BG_BRIGHT_CYAN = "\033[106m"
BG_BRIGHT_WHITE = "\033[107m"

CONFIG_FILE = os.getenv("SW_DEVTOOLS_CONFIG")

class php:
    """Class to handle PHP installation inside SyncWide Devtools."""
    def __init__(self):
        pass

    def install():
        """Downloads and installs PHP 3.14.0 silently."""
        if not is_admin():
            success = request_admin_privileges()
            if success:
                print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
            else:
                print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
            sys.exit(1)

        PHP_url = "https://downloads.php.net/~windows/releases/archives/php-8.5.0-nts-Win32-vs17-x64.zip"
        # Build a proper temp directory for the installer (avoid leading slash on Windows)
        temp_base = os.getenv('TEMP') or os.getenv('TMP') or r"C:\Windows\Temp"
        temp_dir = os.path.join(temp_base, 'sw-devtools')
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
            print(f"{BRIGHT_YELLOW}Could not ensure temp directory '{temp_dir}': {e}{RESET}")
        installer_path = os.path.join(temp_dir, 'php-8.5.0-nts-Win32-vs17-x64.zip')

        try:
            print(f"{BRIGHT_GREEN}Downloading PHP installer from {PHP_url}...{RESET}")
            # Stream the download and display a progress bar
            try:
                with urllib.request.urlopen(PHP_url) as response:
                    total_length = response.getheader('Content-Length')
                    total = int(total_length) if total_length and total_length.isdigit() else 0
                    chunk_size = 8192
                    downloaded = 0
                    bar_length = 40
                    with open(installer_path, 'wb') as out_file:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            out_file.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                percent = downloaded / total
                                filled = int(bar_length * percent)
                                bar = '=' * filled + ' ' * (bar_length - filled)
                                sys.stdout.write(f"\r{BRIGHT_CYAN}Downloading: [{bar}] {percent*100:6.2f}%{RESET}")
                            else:
                                # Unknown total size: show bytes downloaded
                                sys.stdout.write(f"\r{BRIGHT_CYAN}Downloading: {downloaded} bytes{RESET}")
                            sys.stdout.flush()
                sys.stdout.write("\n")
                print(f"{BRIGHT_GREEN}Download complete.{RESET}")
            except Exception:
                # Fall back to urlretrieve if streaming fails for any reason
                print(f"{BRIGHT_YELLOW}Streaming download failed, falling back to simple download...{RESET}")
                urllib.request.urlretrieve(PHP_url, installer_path)
                print(f"{BRIGHT_GREEN}Download complete.{RESET}")
            
            # Notify: checking configuration for install path
            print(f"{BRIGHT_CYAN}Checking configuration for install path...{RESET}")
            install_path = None
            cfg = None
            # Prefer env var, but fallback to default Program Files config location
            config_path_candidate = CONFIG_FILE
            if not config_path_candidate:
                program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                default_cfg = os.path.join(program_files, 'SyncWide Devtools', 'config.json')
                if os.path.exists(default_cfg):
                    config_path_candidate = default_cfg
                    print(f"{BRIGHT_CYAN}Found default config at: {default_cfg}{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}No SW_DEVTOOLS_CONFIG env var and no default config at '{default_cfg}'.{RESET}")

            if config_path_candidate:
                print(f"{BRIGHT_CYAN}Using config file path: {config_path_candidate}{RESET}")
                try:
                    with open(config_path_candidate, 'r', encoding='utf-8') as cfg_file:
                        cfg = json.load(cfg_file)
                        print(f"{BRIGHT_GREEN}Loaded configuration file.{RESET}")
                except FileNotFoundError:
                    print(f"{BRIGHT_YELLOW}Config file not found at '{config_path_candidate}'.{RESET}")
                except json.JSONDecodeError as je:
                    print(f"{BRIGHT_YELLOW}Config file is not valid JSON: {je}{RESET}")
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Could not read config file '{config_path_candidate}': {e}{RESET}")

            if cfg:
                install_path_part = cfg.get('install_path') or cfg.get('php_install_path') or cfg.get('installPath')
                if install_path_part:
                    # If the config points to the SyncWide Devtools folder, append Python314.
                    # Otherwise respect the provided path exactly.
                    normalized = install_path_part.rstrip('\\/ ')
                    base = os.path.basename(normalized).lower()
                    if base in ('syncwide devtools', 'syncwide-devtools'):
                        install_path = os.path.join(install_path_part, 'PHP850')
                        print(f"{BRIGHT_GREEN}Config points to SyncWide Devtools root — using '{install_path}'.{RESET}")
                    else:
                        install_path = install_path_part
                        print(f"{BRIGHT_GREEN}Using install path from config: {install_path}{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}Configuration file did not contain an install path key. Will use default.{RESET}")
            
            if not install_path:
                program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                install_path = os.path.join(program_files, 'SyncWide Devtools', 'PHP850')
                print(f"{BRIGHT_YELLOW}No install path specified in config. Using default: {install_path}{RESET}")
            
            # Ensure the install directory exists (installer will usually create it, but report to user)
            try:
                if not os.path.exists(install_path):
                    os.makedirs(install_path, exist_ok=True)
                    print(f"{BRIGHT_GREEN}Created install directory at '{install_path}'.{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}Install directory already exists at '{install_path}'.{RESET}")
            except Exception as e:
                print(f"{BRIGHT_YELLOW}Could not create install directory '{install_path}': {e}{RESET}")
            
            print(f"{BRIGHT_GREEN}Starting PHP installation to '{install_path}'...{RESET}")

            with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                zip_ref.extractall(install_path)
            print(f"{BRIGHT_GREEN}PHP installed successfully at '{install_path}'.{RESET}")
            
            try:
                os.remove(installer_path)
            except Exception as e:
                print(f"{BRIGHT_YELLOW}Could not delete installer file located at {installer_path}: {e}{RESET}")
            
            add_to_path(install_path, scope='system')  # Requires admin
            print(f"{BRIGHT_GREEN}Added PHP installation directory to system PATH.{RESET}")

            # Write the php_path back into the configuration file so future runs know where PHP is installed
            try:
                # prefer a config path candidate if available, otherwise write a default config under Program Files
                config_to_write = None
                if 'config_path_candidate' in locals() and config_path_candidate:
                    config_to_write = config_path_candidate
                else:
                    program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                    cfg_dir = os.path.join(program_files, 'SyncWide Devtools')
                    try:
                        os.makedirs(cfg_dir, exist_ok=True)
                    except Exception:
                        pass
                    config_to_write = os.path.join(cfg_dir, 'config.json')

                php_exec = os.path.join(install_path, 'php.exe') if install_path else None
                php_path_value = php_exec if php_exec and os.path.exists(php_exec) else install_path

                config_data = {}
                # load existing config if present
                try:
                    if os.path.exists(config_to_write):
                        with open(config_to_write, 'r', encoding='utf-8') as f:
                            try:
                                config_data = json.load(f) or {}
                            except Exception:
                                config_data = {}
                except Exception:
                    config_data = {}

                # set the php_path key
                if php_path_value:
                    config_data['php_path'] = php_path_value
                    try:
                        with open(config_to_write, 'w', encoding='utf-8') as f:
                            json.dump(config_data, f, indent=4)
                        print(f"{BRIGHT_GREEN}Wrote 'php_path' to config at '{config_to_write}'.{RESET}")
                    except Exception as e:
                        print(f"{BRIGHT_YELLOW}Failed to write php_path to config '{config_to_write}': {e}{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}No install path available to write into config.{RESET}")
            except Exception as e:
                print(f"{BRIGHT_YELLOW}Unexpected error while writing config: {e}{RESET}")

        except Exception as e:
            print(f"{BRIGHT_RED}An error occurred during PHP installation: {e}{RESET}")

    def uninstall():
        """Uninstall PHP installed by SyncWide Devtools.
        
        - Determines the installed PHP directory from config (or defaults).
        - Removes the directory and files.
        - Removes the path from the system PATH registry value and broadcasts change.
        - Removes the `php_path` key from the config file.
        """
        if not is_admin():
            success = request_admin_privileges()
            if success:
                print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
            else:
                print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
            sys.exit(1)
        
        print(f"{BRIGHT_CYAN}Starting uninstall of SyncWide-managed PHP...{RESET}")
        
        # Determine config path candidate (prefer env, fallback to Program Files config)
        config_path_candidate = CONFIG_FILE
        if not config_path_candidate:
            program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
            default_cfg = os.path.join(program_files, 'SyncWide Devtools', 'config.json')
            if os.path.exists(default_cfg):
                config_path_candidate = default_cfg
                print(f"{BRIGHT_CYAN}Found default config at: {default_cfg}{RESET}")
            else:
                print(f"{BRIGHT_YELLOW}No SW_DEVTOOLS_CONFIG env var and no default config at '{default_cfg}'.{RESET}")
        
        cfg = {}
        if config_path_candidate and os.path.exists(config_path_candidate):
            try:
                with open(config_path_candidate, 'r', encoding='utf-8') as f:
                    cfg = json.load(f) or {}
                print(f"{BRIGHT_GREEN}Loaded configuration from '{config_path_candidate}'.{RESET}")
            except Exception as e:
                print(f"{BRIGHT_YELLOW}Could not load config '{config_path_candidate}': {e}{RESET}")
        
        # Determine PHP install directory
        php_path_value = cfg.get('php_path') if isinstance(cfg, dict) else None
        if php_path_value:
            # If php_path is an executable, use its containing directory
            if php_path_value.lower().endswith('.exe'):
                target_dir = os.path.dirname(php_path_value)
            else:
                target_dir = php_path_value
        else:
            # fallback to install_path in config (respecting SyncWide Devtools -> PHP850)
            install_path_part = cfg.get('install_path') or cfg.get('php_install_path') or cfg.get('installPath')
            if install_path_part:
                normalized = install_path_part.rstrip('\\/ ')
                base = os.path.basename(normalized).lower()
                if base in ('syncwide devtools', 'syncwide-devtools'):
                    target_dir = os.path.join(install_path_part, 'PHP850')
                else:
                    target_dir = install_path_part
            else:
                # final fallback
                program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                target_dir = os.path.join(program_files, 'SyncWide Devtools', 'PHP850')
        
        target_dir = os.path.abspath(target_dir)
        print(f"{BRIGHT_CYAN}Resolved target uninstall directory: {target_dir}{RESET}")
        
        if not os.path.exists(target_dir):
            print(f"{BRIGHT_YELLOW}Target directory does not exist: {target_dir}. Nothing to remove.{RESET}")
        else:
            # Safety check: ensure we're not deleting a suspicious root path
            unsafe_roots = [os.path.abspath(os.sep).lower(), os.path.abspath(os.environ.get('SystemRoot', r'C:\Windows')).lower()]
            if any(os.path.abspath(target_dir).lower() == r for r in unsafe_roots):
                print(f"{BRIGHT_RED}Refusing to delete unsafe target directory: {target_dir}{RESET}")
            else:
                # Attempt to remove directory tree
                try:
                    print(f"{BRIGHT_CYAN}Removing directory '{target_dir}'...{RESET}")
                    shutil.rmtree(target_dir)
                    print(f"{BRIGHT_GREEN}Removed '{target_dir}'.{RESET}")
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Failed to remove '{target_dir}': {e}{RESET}")
        
        # Remove path from system PATH registry and broadcast change
        try:
            env_key = r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_key, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                try:
                    existing, regtype = winreg.QueryValueEx(key, 'Path')
                except FileNotFoundError:
                    existing = ''
                    regtype = winreg.REG_EXPAND_SZ
                
                parts = [p for p in existing.split(';') if p.strip()]
                # Remove entries equal to or inside target_dir
                new_parts = []
                for p in parts:
                    try:
                        if target_dir and os.path.abspath(p).lower().startswith(os.path.abspath(target_dir).lower() + os.sep):
                            continue
                        if target_dir and os.path.abspath(p).lower() == os.path.abspath(target_dir).lower():
                            continue
                    except Exception:
                        pass
                    new_parts.append(p)
                
                new_value = ';'.join(new_parts)
                if new_value != existing:
                    winreg.SetValueEx(key, 'Path', 0, regtype, new_value)
                    HWND_BROADCAST = 0xFFFF
                    WM_SETTINGCHANGE = 0x001A
                    SMTO_ABORTIFHUNG = 0x0002
                    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, None)
                    print(f"{BRIGHT_GREEN}Removed '{target_dir}' from system PATH.{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}No PATH entries matched '{target_dir}'.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_YELLOW}Could not update system PATH: {e}{RESET}")
        
        # Remove 'php_path' from config file (if present)
        try:
            config_to_write = config_path_candidate if (config_path_candidate and os.path.exists(config_path_candidate)) else None
            if not config_to_write:
                program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                cfg_dir = os.path.join(program_files, 'SyncWide Devtools')
                try:
                    os.makedirs(cfg_dir, exist_ok=True)
                except Exception:
                    pass
                config_to_write = os.path.join(cfg_dir, 'config.json')
            
            config_data = {}
            if os.path.exists(config_to_write):
                try:
                    with open(config_to_write, 'r', encoding='utf-8') as f:
                        config_data = json.load(f) or {}
                except Exception:
                    config_data = {}
            
            if isinstance(config_data, dict) and 'php_path' in config_data:
                del config_data['php_path']
                try:
                    with open(config_to_write, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=4)
                    print(f"{BRIGHT_GREEN}Removed 'php_path' from config at '{config_to_write}'.{RESET}")
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Failed to update config file '{config_to_write}': {e}{RESET}")
            else:
                print(f"{BRIGHT_YELLOW}No 'php_path' key found in config to remove.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_YELLOW}Unexpected error while updating config: {e}{RESET}")
        
        print(f"{BRIGHT_GREEN}Uninstall completed (see messages above).{RESET}")

    def status():
        """Check and display the status of the PHP installation."""
        print(f"{BRIGHT_CYAN}Checking PHP installation status...{RESET}\n")
        
        # Determine config path
        config_path_candidate = CONFIG_FILE
        if not config_path_candidate:
            program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
            default_cfg = os.path.join(program_files, 'SyncWide Devtools', 'config.json')
            if os.path.exists(default_cfg):
                config_path_candidate = default_cfg
        
        # Load configuration
        cfg = {}
        if config_path_candidate and os.path.exists(config_path_candidate):
            try:
                with open(config_path_candidate, 'r', encoding='utf-8') as f:
                    cfg = json.load(f) or {}
            except Exception as e:
                print(f"{BRIGHT_YELLOW}Could not load config: {e}{RESET}")
        
        # Get PHP path from config
        php_path_value = cfg.get('php_path') if isinstance(cfg, dict) else None
        
        if not php_path_value:
            print(f"{BRIGHT_RED}✗ PHP is not installed via SyncWide Devtools{RESET}")
            print(f"  No 'php_path' found in configuration.\n")
            return
        
        # Determine installation directory
        if php_path_value.lower().endswith('.exe'):
            install_dir = os.path.dirname(php_path_value)
            php_exe = php_path_value
        else:
            install_dir = php_path_value
            php_exe = os.path.join(install_dir, 'php.exe')
        
        # Check if directory exists
        if not os.path.exists(install_dir):
            print(f"{BRIGHT_RED}✗ PHP installation directory not found{RESET}")
            print(f"  Expected: {install_dir}\n")
            return
        
        # Check if executable exists
        if not os.path.exists(php_exe):
            print(f"{BRIGHT_YELLOW}⚠ PHP directory exists but php.exe not found{RESET}")
            print(f"  Directory: {install_dir}")
            print(f"  Expected executable: {php_exe}\n")
            return
        
        # Try to get version
        version_info = "Unknown"
        try:
            result = subprocess.run(
                [php_exe, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # PHP version is typically in the first line
                first_line = result.stdout.split('\n')[0] if result.stdout else ''
                version_info = first_line.strip()
        except Exception:
            pass
        
        # Check if in PATH
        in_path = False
        try:
            env_key = r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_key, 0, winreg.KEY_READ) as key:
                try:
                    path_value, _ = winreg.QueryValueEx(key, 'Path')
                    path_parts = [p.strip().lower() for p in path_value.split(';') if p.strip()]
                    in_path = any(os.path.abspath(install_dir).lower() == os.path.abspath(p).lower() for p in path_parts)
                except Exception:
                    pass
        except Exception:
            pass
        
        # Display status
        print(f"{BRIGHT_GREEN}✓ PHP is installed{RESET}")
        print(f"  Version: {BRIGHT_CYAN}{version_info}{RESET}")
        print(f"  Location: {BRIGHT_CYAN}{install_dir}{RESET}")
        print(f"  Executable: {BRIGHT_CYAN}{php_exe}{RESET}")
        print(f"  In System PATH: {BRIGHT_GREEN + 'Yes' + RESET if in_path else BRIGHT_YELLOW + 'No' + RESET}")
        
        if config_path_candidate:
            print(f"  Config: {BRIGHT_CYAN}{config_path_candidate}{RESET}")
        print()