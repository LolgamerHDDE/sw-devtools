import os
import sys
import argparse
from functions.initialize import init_default_conifg, init_default_conifg_ud
from functions.python import python
from functions.php import php

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

def main():
    print(f"""{BRIGHT_CYAN}SyncWide Solutions Developer Tools (Version: 0.0.1b){RESET}

""")

    parser = argparse.ArgumentParser(description='SyncWide Solutions Developer Tools')
    
    parser.add_argument('--version', action='store_true', help='Show the version of the tool')
    parser.add_argument('--install', '-i', help='Install requested packages', type=str)
    parser.add_argument('--uninstall', '-u', help='Uninstall requested packages', type=str)
    parser.add_argument('--init', help='Initialize configuration for faster Command execution')
    parser.add_argument('--status', help='Show the status of requested packages', type=str)

    args = parser.parse_args()

    if args.version:
        print(f"{BRIGHT_CYAN}Version: {GREEN}0.0.1b{RESET}")
        sys.exit(0)

    if args.init is not None:
        if args.init == 'default':
            try:
                init_default_conifg()
                print(f"{BRIGHT_GREEN}Initialization complete.{RESET}")
            except Exception as e:
                print(f"{BRIGHT_RED}Error during initialization: {e}{RESET}")
        else:
            try:
                init_default_conifg_ud(args.init)
                print(f"{BRIGHT_GREEN}Initialization complete.{RESET}")
            except Exception as e:
                print(f"{BRIGHT_RED}Error during initialization: {e}{RESET}")
        sys.exit(0)
    
    if args.install is not None:
        if args.install.lower() == 'python':
            python.install()
        if args.install.lower() == 'php':
            php.install()

    if args.uninstall is not None:
        if args.uninstall.lower() == 'python':
            python.uninstall()
        if args.uninstall.lower() == 'php':
            php.uninstall()
    
    if args.status is not None:
        if args.status.lower() == 'python':
            python.status()
        if args.status.lower() == 'php':
            php.status()

if __name__ == "__main__":
    main()