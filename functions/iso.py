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

def read_isos_config():
    """Read and return the isos.json configuration file.
    
    Returns:
        dict: The parsed JSON data from isos.json, or None if the file cannot be read.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'isos.json')
        
        if not os.path.exists(file_path):
            print(f"{BRIGHT_RED}ISO configuration file not found at: {file_path}{RESET}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            iso_data = json.load(f)
        
        return iso_data
    except json.JSONDecodeError as e:
        print(f"{BRIGHT_RED}Failed to parse isos.json: {e}{RESET}")
        return None
    except Exception as e:
        print(f"{BRIGHT_RED}Error reading isos.json: {e}{RESET}")
        return None

def list_available_isos():
    """List all available ISO options from the configuration."""
    iso_data = read_isos_config()
    if iso_data is None:
        return
    
    print(f"\n{BRIGHT_CYAN}{BOLD}Available ISO Downloads:{RESET}\n")
    
    for os_category, os_content in iso_data.items():
        print(f"{BRIGHT_GREEN}{os_category.upper()}{RESET}")
        _print_iso_tree(os_content, indent=1)
        print()

def _print_iso_tree(data, indent=0):
    """Recursively print the ISO tree structure."""
    prefix = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict):
                # Check if this dict contains ISO URLs (leaf node)
                has_urls = any(isinstance(v, str) and v.startswith('http') for v in value.values())
                if has_urls:
                    print(f"{prefix}{BRIGHT_YELLOW}├─{RESET} {key}")
                    for sub_key, url in value.items():
                        if isinstance(url, str) and url.startswith('http'):
                            print(f"{prefix}  {BRIGHT_CYAN}└─{RESET} {sub_key}: {BRIGHT_WHITE}{url[:60]}...{RESET}")
                else:
                    print(f"{prefix}{BRIGHT_YELLOW}├─{RESET} {key}")
                    _print_iso_tree(value, indent + 1)
            else:
                print(f"{prefix}{BRIGHT_CYAN}└─{RESET} {key}: {value}")

def get_iso_url(path: str, language: str = "en_US"):
    """Get a specific ISO URL from the configuration using a path string.
    
    Args:
        path: Path to the ISO in format 'os_category/distro/version/iso_type'
              Examples: 
                - 'windows/11/media_creation_tool_download'
                - 'linux/ubuntu/24.04_lts/desktop_amd64'
                - 'bsd/freebsd/14.2/dvd_x86_64'
        language: Language code (default: 'en_US')
    
    Returns:
        tuple: (url, note) if found, (None, None) otherwise
    """
    iso_data = read_isos_config()
    if iso_data is None:
        return None, None
    
    try:
        parts = path.split('/')
        if len(parts) < 3:
            print(f"{BRIGHT_RED}Invalid path format. Expected: 'os_category/distro/version/iso_type'{RESET}")
            return None, None
        
        # Navigate through the JSON structure
        current = iso_data
        for part in parts[:-1]:  # Navigate to the version level
            current = current[part]
        
        # Get language data
        if language not in current:
            print(f"{BRIGHT_YELLOW}Language '{language}' not found, falling back to en_US{RESET}")
            language = "en_US"
            if language not in current:
                print(f"{BRIGHT_RED}No en_US fallback available{RESET}")
                return None, None
        
        lang_data = current[language]
        iso_type = parts[-1]
        
        # Get URL and optional note
        url = lang_data.get(iso_type)
        note = lang_data.get('note', None)
        
        if isinstance(url, str) and url.startswith('http'):
            return url, note
        else:
            print(f"{BRIGHT_RED}Invalid or missing URL in configuration{RESET}")
            return None, None
            
    except KeyError as e:
        print(f"{BRIGHT_RED}Path not found in configuration: {e}{RESET}")
        return None, None
    except Exception as e:
        print(f"{BRIGHT_RED}Error parsing path: {e}{RESET}")
        return None, None

def download_iso(path: str, language: str = "en_US"):
    """Download an ISO image using a simple path and language.
    
    Args:
        path: Path to the ISO in format 'os_category/distro/version/iso_type'
              Examples: 
                - 'windows/11/media_creation_tool_download'
                - 'linux/ubuntu/24.04_lts/desktop_amd64'
                - 'linux/fedora/workstation/live_iso'
                - 'bsd/freebsd/14.2/dvd_x86_64'
        language: Language code (default: 'en_US')
                  Supported: en_US, de_DE, fr_FR, es_ES, it_IT, ja_JP, zh_CN, ru_RU, etc.
    """
    print(f"{BRIGHT_CYAN}Preparing to download ISO...{RESET}\n")
    
    # Get the ISO URL and note
    iso_url, note = get_iso_url(path, language)
    if iso_url is None:
        print(f"{BRIGHT_RED}Failed to retrieve ISO URL{RESET}")
        sys.exit(1)
    
    # Display note if available
    if note:
        print(f"{BRIGHT_YELLOW}Note: {note}{RESET}\n")
    
    # Determine output directory (user's Downloads folder)
    output_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"{BRIGHT_RED}Failed to create output directory: {e}{RESET}")
        sys.exit(1)
    
    # Extract filename from URL
    filename = os.path.basename(iso_url.split('?')[0])
    if not filename.endswith('.iso'):
        # Generate filename from path
        safe_path = path.replace('/', '_').replace('\\', '_')
        filename = f"{safe_path}_{language}.iso"
    
    output_path = os.path.join(output_dir, filename)
    
    print(f"{BRIGHT_GREEN}Downloading from:{RESET} {iso_url}")
    print(f"{BRIGHT_GREEN}Saving to:{RESET} {output_path}\n")
    
    try:
        # Stream download with progress bar
        with urllib.request.urlopen(iso_url) as response:
            total_length = response.getheader('Content-Length')
            total = int(total_length) if total_length and total_length.isdigit() else 0
            chunk_size = 8192
            downloaded = 0
            bar_length = 40
            
            with open(output_path, 'wb') as out_file:
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
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total / (1024 * 1024)
                        sys.stdout.write(f"\r{BRIGHT_CYAN}[{bar}] {percent*100:6.2f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB){RESET}")
                    else:
                        mb_downloaded = downloaded / (1024 * 1024)
                        sys.stdout.write(f"\r{BRIGHT_CYAN}Downloaded: {mb_downloaded:.1f} MB{RESET}")
                    sys.stdout.flush()
        
        sys.stdout.write("\n")
        print(f"\n{BRIGHT_GREEN}✓ Download completed successfully!{RESET}")
        print(f"{BRIGHT_GREEN}ISO saved to:{RESET} {output_path}")
        
    except urllib.error.URLError as e:
        print(f"\n{BRIGHT_RED}Download failed: {e}{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{BRIGHT_RED}An error occurred: {e}{RESET}")
        sys.exit(1)
