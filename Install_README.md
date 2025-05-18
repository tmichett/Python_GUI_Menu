# RHCI Foundation Instructor Toolkit - Installation Guide

A GUI application for managing RHCI Foundation tasks and configurations.

## Building the Application

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Required Python Packages
```bash
pip install pyinstaller PyQt5 pyyaml
```

### Build Steps
1. Clone or download this repository
2. Navigate to the project directory
3. Run PyInstaller with the provided spec file:
```bash
pyinstaller menu.spec
```

## Installation

### Required Files
After building, you'll need the following files in your target directory:
- `RHCI_Toolkit` (the binary from the `dist` directory)
- `config.yml` (your configuration file)
- `logo.png` (your logo image)
- `smallicon.png` (your application icon)

### Installation Steps
1. Copy the `RHCI_Toolkit` binary from the `dist` directory to your target location
2. Copy your `config.yml`, `logo.png`, and `smallicon.png` files to the same directory as the binary
3. Make the binary executable:
```bash
chmod +x RHCI_Toolkit
```

## Running the Application

### Standard Run
To run the application with the default config.yml in the same directory:
```bash
./RHCI_Toolkit
```

### Custom Config
To run the application with a different config file:
```bash
./RHCI_Toolkit /path/to/custom/config.yml
```

## Configuration
The application uses an external `config.yml` file for configuration. You can modify this file without rebuilding the application. The config file should be in the same directory as the executable.

### Config File Structure
```yaml
icon: smallicon.png
logo: logo.png
logo_size: 320x240
menu_title: RHCI Foundation Instructor Toolkit
num_columns: 2

menu_items:
  - name: Menu Name
    column: 1
    button_info: "Menu description"
    items:
      - name: Command Name
        command: "command to execute"
        button_info: "Command description"
```

## Support
For issues or questions, please contact the development team. 