# SyncWide Developer Tools

![Version](https://img.shields.io/badge/version-0.0.1b-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Python](https://img.shields.io/badge/python-3.x-green)

A powerful command-line tool for managing development environments on Windows, specifically designed to simplify the installation and management of Python and PHP runtimes.

## 📋 Overview

SyncWide Developer Tools (sw-devtools) automates the installation, configuration, and management of development tools on Windows systems. It handles administrative privileges, system PATH management, and maintains configuration files for seamless development environment setup.

## ✨ Features

- **Automated Python Installation**: Install Python 3.14.0 with automatic PATH configuration
- **Automated PHP Installation**: Install PHP 8.5.0 NTS with system integration
- **Admin Privilege Management**: Automatic UAC elevation when required
- **Configuration Management**: Centralized config file with environment variable support
- **System PATH Integration**: Automatic PATH registry updates with environment broadcasting
- **Progress Tracking**: Real-time download progress bars
- **Fallback Mechanisms**: Embeddable Python extraction if standard installation fails
- **Clean Uninstallation**: Complete removal of installed runtimes and PATH entries

## 🚀 Getting Started

### Prerequisites

- Windows operating system
- Administrator privileges (automatically requested when needed)
- Internet connection for downloading packages

### Installation

Clone the repository:

```bash
git clone https://github.com/LolgamerHDDE/sw-devtools.git
cd sw-devtools
```

### Configuration

Initialize the default configuration:

```bash
python main.py --init default
```

Or specify a custom installation directory:

```bash
python main.py --init "C:\CustomPath\SyncWide Devtools"
```

#### Environment Variable

Set the `SW_DEVTOOLS_CONFIG` environment variable to point to your configuration file:

```powershell
$env:SW_DEVTOOLS_CONFIG = "C:\Path\To\config.json"
```

If not set, the tool defaults to: `C:\Program Files\SyncWide Devtools\config.json`

## 📖 Usage

### Display Version

```bash
python main.py --version
```

### Initialize Configuration

```bash
# Use default Program Files location
python main.py --init default

# Use custom directory
python main.py --init "C:\Custom\Path"
```

### Install Packages

Install Python:
```bash
python main.py --install python
# or
python main.py -i python
```

Install PHP:
```bash
python main.py --install php
# or
python main.py -i php
```

### Uninstall Packages

Uninstall Python:
```bash
python main.py --uninstall python
# or
python main.py -u python
```

Uninstall PHP:
```bash
python main.py --uninstall php
# or
python main.py -u php
```

## 🗂️ Project Structure

```
syncwide-devtools/
│
├── main.py                 # Main entry point and CLI interface
├── functions/              # Core functionality modules
│   ├── __init__.py         # Package initialization
│   ├── admin.py            # Admin privilege handling
│   ├── initialize.py       # Configuration initialization
│   ├── path.py             # PATH management utilities
│   ├── php.py              # PHP installation/uninstallation
│   └── python.py           # Python installation/uninstallation
└── README.md               # This file
```

## ⚙️ Configuration File

The configuration file (`config.json`) supports the following keys:

```json
{
    "install_path": "C:\\Program Files\\SyncWide Devtools",
    "python_path": "C:\\Program Files\\Python314\\python.exe",
    "php_path": "C:\\Program Files\\PHP85\\php.exe"
}
```

- **install_path**: Base directory for SyncWide Devtools installations
- **python_path**: Path to the installed Python executable (auto-populated)
- **php_path**: Path to the installed PHP executable (auto-populated)

## 🔧 Technical Details

### Python Installation

- **Version**: Python 3.14.0 (64-bit)
- **Installation Method**: Silent installation with system-wide configuration
- **Default Location**: `C:\Program Files\Python314`
- **Features**: 
  - Adds to PATH automatically
  - Excludes test suite
  - Installs for all users
  - Falls back to embeddable distribution if needed

### PHP Installation

- **Version**: PHP 8.5.0 NTS (Non-Thread Safe, 64-bit)
- **Installation Method**: ZIP extraction
- **Default Location**: `C:\Program Files\PHP85`
- **Features**:
  - Automatic PATH configuration
  - System-wide availability

### Admin Privileges

The tool uses Windows API calls to:
- Detect current privilege level (`IsUserAnAdmin`)
- Request UAC elevation when needed (`ShellExecuteW`)
- Modify system registry for PATH management
- Broadcast environment changes to running processes

## 🎨 CLI Features

- **Colorized Output**: Uses ANSI escape codes for enhanced readability
- **Progress Bars**: Real-time download progress with percentage and visual bar
- **Error Handling**: Comprehensive error messages with color-coded severity
- **Verbose Logging**: Detailed step-by-step operation feedback

## 🛡️ Safety Features

- Path validation to prevent accidental system directory deletion
- Registry backup via read before write
- Environment change broadcasting to update running processes
- Configuration file validation and error recovery
- Graceful fallback mechanisms

## 🐛 Troubleshooting

### Installation Fails

1. Ensure you have administrator privileges
2. Check your internet connection
3. Verify available disk space
4. Review the console output for specific error messages

### PATH Not Updated

1. Restart your terminal/command prompt
2. Check if the path was added to system PATH in registry
3. Log out and back in to refresh environment variables

### Configuration Not Found

1. Verify `SW_DEVTOOLS_CONFIG` environment variable
2. Check default location: `C:\Program Files\SyncWide Devtools\config.json`
3. Run `--init default` to recreate configuration

## 📄 License

Copyright © 2025 SyncWide Solutions. All rights reserved.

## 👥 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📧 Contact

For support or inquiries, please contact SyncWide Solutions.

## 🗺️ Roadmap

- [ ] Add support for Node.js installation
- [ ] Implement version management for installed packages
- [ ] Add support for virtual environment management
- [ ] Add support for Linux and macOS
- [ ] Package management integration (pip, composer)

---

**Note**: This is a beta version (0.0.1b). Features and functionality may change in future releases.
