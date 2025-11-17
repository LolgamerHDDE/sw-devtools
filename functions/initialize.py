import os
import sys
import json
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

def init_default_conifg():
    if not is_admin():
        success = request_admin_privileges()
        if success:
            print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
        else:
            print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
        sys.exit(1)

    program_files = os.environ.get('ProgramFiles', r'C:\Program Files')
    default_directory = os.path.join(program_files, 'SyncWide Devtools')

    if not os.path.exists(default_directory):
        try:
            os.makedirs(default_directory)
            print(f"{BRIGHT_GREEN}Created default directory at {default_directory}{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}Failed to create default directory: {e}{RESET}")
            sys.exit(1)
    else:
        print(f"{BRIGHT_YELLOW}Default directory already exists at {default_directory}{RESET}")

    if not os.path.exists(os.path.join(default_directory, "config.json")):
        try:
            config_path = os.path.join(default_directory, "config.json")
            with open(config_path, 'w', encoding='utf-8') as config_file:
                json.dump({"install_path": default_directory}, config_file, indent=4)
            print(f"{BRIGHT_GREEN}Initialized configuration file at {config_path}.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}Failed to create configuration file: {e}{RESET}")
    else:
        print(f"{BRIGHT_YELLOW}Configuration file already exists.{RESET}")
        
def init_default_conifg_ud(path: str):
    if not is_admin():
        success = request_admin_privileges()
        if success:
            print(f"{BRIGHT_YELLOW}Requested admin privileges. Relaunching...{RESET}")
        else:
            print(f"{BRIGHT_RED}Admin privilege request was denied.{RESET}")
        sys.exit(1)

    # If a custom path is provided, create the SyncWide Devtools folder inside it.
    default_directory = os.path.join(os.path.abspath(path), 'SyncWide Devtools')

    if not os.path.exists(default_directory):
        try:
            os.makedirs(default_directory)
            print(f"{BRIGHT_GREEN}Created default directory at {default_directory}{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}Failed to create default directory: {e}{RESET}")
            sys.exit(1)
    else:
        print(f"{BRIGHT_YELLOW}Default directory already exists at {default_directory}{RESET}")

    if not os.path.exists(os.path.join(default_directory, "config.json")):
        try:
            config_path = os.path.join(default_directory, "config.json")
            with open(config_path, 'w', encoding='utf-8') as config_file:
                json.dump({"install_path": default_directory}, config_file, indent=4)
            print(f"{BRIGHT_GREEN}Initialized configuration file at {config_path}.{RESET}")
        except Exception as e:
            print(f"{BRIGHT_RED}Failed to create configuration file: {e}{RESET}")
    else:
        print(f"{BRIGHT_YELLOW}Configuration file already exists.{RESET}")
        