import os
import sys
import subprocess
import urllib.request
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

class python:
    """Class to handle Python installation inside SyncWide Devtools."""
    def __init__(self):
        pass

    def install(self):
        """Downloads and installs Python 3.14.0 silently."""
        if not is_admin():
            success = request_admin_privileges()
            if success:
                print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
            else:
                print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
            sys.exit(1)

        python_url = "https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe"
        installer_path = os.path.join(os.getenv('TEMP'), 'python-3.14.0-amd64.exe')

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

            print(f"{BRIGHT_GREEN}Starting Python installation...{RESET}")
            install_command = f'"{installer_path}" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0'
            process = subprocess.run(install_command, shell=True)
            if process.returncode == 0:
                try:
                    os.remove(installer_path)
                except Exception as e:
                    print(f"{BRIGHT_YELLOW}Could not delete installer file located at {installer_path}: {e}{RESET}")
                print(f"{BRIGHT_GREEN}Python installed successfully.{RESET}")
            else:
                print(f"{BRIGHT_RED}Python installation failed with return code {process.returncode}.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}An error occurred during Python installation: {e}{RESET}")