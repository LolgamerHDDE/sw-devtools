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

class python:
    """Class to handle Python installation inside SyncWide Devtools."""
    def __init__(self):
        pass

    def install():
        """Downloads and installs Python 3.14.0 silently."""
        if not is_admin():
            success = request_admin_privileges()
            if success:
                print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
            else:
                print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
            sys.exit(1)

        python_url = "https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe"
        # Build a proper temp directory for the installer (avoid leading slash on Windows)
        temp_base = os.getenv('TEMP') or os.getenv('TMP') or r"C:\Windows\Temp"
        temp_dir = os.path.join(temp_base, 'sw-devtools')
        try:
            os.makedirs(temp_dir, exist_ok=True)
        except Exception as e:
            print(f"{BRIGHT_YELLOW}Could not ensure temp directory '{temp_dir}': {e}{RESET}")
        installer_path = os.path.join(temp_dir, 'python-3.14.0-amd64.exe')

        try:
            print(f"{BRIGHT_GREEN}Downloading Python installer from {python_url}...{RESET}")
            # Stream the download and display a progress bar
            try:
                with urllib.request.urlopen(python_url) as response:
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
                urllib.request.urlretrieve(python_url, installer_path)
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
                install_path_part = cfg.get('install_path') or cfg.get('python_install_path') or cfg.get('installPath')
                if install_path_part:
                    # If the config points to the SyncWide Devtools folder, append Python314.
                    # Otherwise respect the provided path exactly.
                    normalized = install_path_part.rstrip('\\/ ')
                    base = os.path.basename(normalized).lower()
                    if base in ('syncwide devtools', 'syncwide-devtools'):
                        install_path = os.path.join(install_path_part, 'Python314')
                        print(f"{BRIGHT_GREEN}Config points to SyncWide Devtools root — using '{install_path}'.{RESET}")
                    else:
                        install_path = install_path_part
                        print(f"{BRIGHT_GREEN}Using install path from config: {install_path}{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}Configuration file did not contain an install path key. Will use default.{RESET}")

            # Fallback to Program Files if not provided
            if not install_path:
                program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                install_path = os.path.join(program_files, "Python314")
                print(f"{BRIGHT_YELLOW}Falling back to default install path: {install_path}{RESET}")

            # Ensure the install directory exists (installer will usually create it, but report to user)
            try:
                if not os.path.exists(install_path):
                    os.makedirs(install_path, exist_ok=True)
                    print(f"{BRIGHT_GREEN}Created install directory at '{install_path}'.{RESET}")
                else:
                    print(f"{BRIGHT_YELLOW}Install directory already exists at '{install_path}'.{RESET}")
            except Exception as e:
                print(f"{BRIGHT_YELLOW}Could not create install directory '{install_path}': {e}{RESET}")

            print(f"{BRIGHT_GREEN}Starting Python installation to '{install_path}'...{RESET}")
            install_command = f'"{installer_path}" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 TargetDir="{install_path}"'
            process = subprocess.run(install_command, shell=True)
            if process.returncode == 0:
                try:
                    os.remove(installer_path)
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Could not delete installer file located at {installer_path}: {e}{RESET}")
                print(f"{BRIGHT_GREEN}Python installer reported success.{RESET}")

                # Verify that installation produced usable files in the target directory
                try:
                    contents = os.listdir(install_path)
                except Exception:
                    contents = []

                has_python_exe = any(name.lower().startswith('python') and name.lower().endswith('.exe') for name in contents)
                has_lib = any(name.lower() == 'lib' for name in contents)

                if not contents or (not has_python_exe and not has_lib):
                    print(f"{BRIGHT_YELLOW}Target install directory appears empty or missing Python files. Falling back to embeddable zip extraction...{RESET}")
                    embed_url = "https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-amd64.zip"
                    embed_zip_path = os.path.join(temp_dir, 'python-3.14.0-embed-amd64.zip')
                    try:
                        print(f"{BRIGHT_GREEN}Downloading embeddable Python zip from {embed_url}...{RESET}")
                        urllib.request.urlretrieve(embed_url, embed_zip_path)
                        print(f"{BRIGHT_GREEN}Download complete. Extracting to '{install_path}'...{RESET}")
                        with zipfile.ZipFile(embed_zip_path, 'r') as zf:
                            zf.extractall(install_path)
                        try:
                            os.remove(embed_zip_path)
                        except Exception:
                            pass
                        print(f"{BRIGHT_GREEN}Embeddable Python extracted to '{install_path}'.{RESET}")
                    except Exception as e:
                        print(f"{BRIGHT_RED}Failed to extract embeddable Python: {e}{RESET}")
                else:
                    print(f"{BRIGHT_GREEN}Python installed successfully.{RESET}")
                # Attempt to add the installed folder to the system PATH so new shells pick it up
                def add_path_to_system_path(path_to_add: str) -> bool:
                    try:
                        # Read current system Path
                        env_key = r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, env_key, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                            try:
                                existing, regtype = winreg.QueryValueEx(key, 'Path')
                            except FileNotFoundError:
                                existing = ''
                                regtype = winreg.REG_EXPAND_SZ

                            parts = [p.strip() for p in existing.split(';') if p.strip()]
                            normalized_parts = [p.lower() for p in parts]
                            if path_to_add.lower() in normalized_parts:
                                return False

                            new_path = existing + (';' if existing and not existing.endswith(';') else '') + path_to_add
                            winreg.SetValueEx(key, 'Path', 0, regtype, new_path)

                        # Broadcast environment change so other processes can see it
                        HWND_BROADCAST = 0xFFFF
                        WM_SETTINGCHANGE = 0x001A
                        SMTO_ABORTIFHUNG = 0x0002
                        ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, None)
                        return True
                    except Exception as e:
                        print(f"{BRIGHT_YELLOW}Could not update system PATH: {e}{RESET}")
                        return False

                # Update current process PATH immediately
                try:
                    if install_path and os.path.isdir(install_path):
                        if install_path not in os.environ.get('PATH', ''):
                            os.environ['PATH'] = install_path + os.pathsep + os.environ.get('PATH', '')
                        added = add_path_to_system_path(install_path)
                        if added:
                            print(f"{BRIGHT_GREEN}Added '{install_path}' to system PATH.{RESET}")
                        else:
                            print(f"{BRIGHT_YELLOW}'{install_path}' already present in system PATH or could not be added.{RESET}")
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Failed to update process PATH: {e}{RESET}")

                # Write the python_path back into the configuration file so future runs know where Python is installed
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

                    python_exec = os.path.join(install_path, 'python.exe') if install_path else None
                    python_path_value = python_exec if python_exec and os.path.exists(python_exec) else install_path

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

                    # set the python_path key
                    if python_path_value:
                        config_data['python_path'] = python_path_value
                        try:
                            with open(config_to_write, 'w', encoding='utf-8') as f:
                                json.dump(config_data, f, indent=4)
                            print(f"{BRIGHT_GREEN}Wrote 'python_path' to config at '{config_to_write}'.{RESET}")
                        except Exception as e:
                            print(f"{BRIGHT_YELLOW}Failed to write python_path to config '{config_to_write}': {e}{RESET}")
                    else:
                        print(f"{BRIGHT_YELLOW}No install path available to write into config.{RESET}")
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Unexpected error while writing config: {e}{RESET}")
            else:
                print(f"{BRIGHT_RED}Python installation failed with return code {process.returncode}.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}An error occurred during Python installation: {e}{RESET}")

    def uninstall():
        """Uninstall Python installed by SyncWide Devtools.

        - Determines the installed python directory from config (or defaults).
        - Removes the directory and files.
        - Removes the path from the system PATH registry value and broadcasts change.
        - Removes the `python_path` key from the config file.
        """
        if not is_admin():
            success = request_admin_privileges()
            if success:
                print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
            else:
                print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
            sys.exit(1)

        print(f"{BRIGHT_CYAN}Starting uninstall of SyncWide-managed Python...{RESET}")

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

        # Determine python install directory
        python_path_value = cfg.get('python_path') if isinstance(cfg, dict) else None
        if python_path_value:
            # If python_path is an executable, use its containing directory
            if python_path_value.lower().endswith('.exe'):
                target_dir = os.path.dirname(python_path_value)
            else:
                target_dir = python_path_value
        else:
            # fallback to install_path in config (respecting SyncWide Devtools -> Python314)
            install_path_part = cfg.get('install_path') or cfg.get('python_install_path') or cfg.get('installPath')
            if install_path_part:
                normalized = install_path_part.rstrip('\\/ ')
                base = os.path.basename(normalized).lower()
                if base in ('syncwide devtools', 'syncwide-devtools'):
                    target_dir = os.path.join(install_path_part, 'Python314')
                else:
                    target_dir = install_path_part
            else:
                # final fallback
                program_files = os.getenv('ProgramFiles') or r"C:\Program Files"
                target_dir = os.path.join(program_files, 'Python314')

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

        # Remove 'python_path' from config file (if present)
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

            if isinstance(config_data, dict) and 'python_path' in config_data:
                del config_data['python_path']
                try:
                    with open(config_to_write, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=4)
                    print(f"{BRIGHT_GREEN}Removed 'python_path' from config at '{config_to_write}'.{RESET}")
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Failed to update config file '{config_to_write}': {e}{RESET}")
            else:
                print(f"{BRIGHT_YELLOW}No 'python_path' key found in config to remove.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_YELLOW}Unexpected error while updating config: {e}{RESET}")

        print(f"{BRIGHT_GREEN}Uninstall completed (see messages above).{RESET}")

    def status():
        """Check and display the status of the Python installation."""
        print(f"{BRIGHT_CYAN}Checking Python installation status...{RESET}\n")
        
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
        
        # Get python path from config
        python_path_value = cfg.get('python_path') if isinstance(cfg, dict) else None
        
        if not python_path_value:
            print(f"{BRIGHT_RED}✗ Python is not installed via SyncWide Devtools{RESET}")
            print(f"  No 'python_path' found in configuration.\n")
            return
        
        # Determine installation directory
        if python_path_value.lower().endswith('.exe'):
            install_dir = os.path.dirname(python_path_value)
            python_exe = python_path_value
        else:
            install_dir = python_path_value
            python_exe = os.path.join(install_dir, 'python.exe')
        
        # Check if directory exists
        if not os.path.exists(install_dir):
            print(f"{BRIGHT_RED}✗ Python installation directory not found{RESET}")
            print(f"  Expected: {install_dir}\n")
            return
        
        # Check if executable exists
        if not os.path.exists(python_exe):
            print(f"{BRIGHT_YELLOW}⚠ Python directory exists but python.exe not found{RESET}")
            print(f"  Directory: {install_dir}")
            print(f"  Expected executable: {python_exe}\n")
            return
        
        # Try to get version
        version_info = "Unknown"
        try:
            result = subprocess.run(
                [python_exe, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_info = result.stdout.strip() or result.stderr.strip()
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
        print(f"{BRIGHT_GREEN}✓ Python is installed{RESET}")
        print(f"  Version: {BRIGHT_CYAN}{version_info}{RESET}")
        print(f"  Location: {BRIGHT_CYAN}{install_dir}{RESET}")
        print(f"  Executable: {BRIGHT_CYAN}{python_exe}{RESET}")
        print(f"  In System PATH: {BRIGHT_GREEN + 'Yes' + RESET if in_path else BRIGHT_YELLOW + 'No' + RESET}")
        
        if config_path_candidate:
            print(f"  Config: {BRIGHT_CYAN}{config_path_candidate}{RESET}")
        print()
