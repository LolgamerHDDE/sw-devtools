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
            with open(config_path_candidate, 'w', encoding='utf-8') as config_file:
                json.dump({"php_install_path": install_path}, config_file, indent=4)
            os.environ["SW_DEVTOOLS_CONFIG"] = config_path_candidate
            print(f"{BRIGHT_GREEN}Initialized configuration file at {config_path_candidate}.{RESET}")
            add_to_path(install_path, scope='system')  # Requires admin
            print(f"{BRIGHT_GREEN}Added PHP installation directory to system PATH.{RESET}")

        except Exception as e:
            print(f"{BRIGHT_RED}An error occurred during PHP installation: {e}{RESET}")