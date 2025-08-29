# Building the Python GUI Menu Application

This document explains how to build a self-contained executable of the Python GUI Menu application that doesn't require virtual environments or Python installations on the target system.

## Overview

The build process uses PyInstaller to create a standalone executable that bundles all Python dependencies and includes the necessary configuration and asset files (icons, logos, config.yml).

## Prerequisites

- Python 3.8 or later
- pip package manager
- Internet connection (for downloading PyInstaller and dependencies)

## Build Options

You have three ways to build the application:

### Option 1: Python Build Script (Recommended - Cross-platform)

```bash
# Make sure you have the requirements file
python build.py
```

This is the most portable option that works on Windows, macOS, and Linux.

### Option 2: Shell Script (Unix/Linux/macOS)

```bash
# Make executable (if needed)
chmod +x build.sh

# Run the build
./build.sh
```

### Option 3: Batch Script (Windows)

```cmd
build.bat
```

## Build Process

All build scripts perform the following steps:

1. **Prerequisites Check**: Verify Python and pip are installed
2. **Clean Previous Builds**: Remove old build artifacts
3. **Create Build Environment**: Set up a temporary virtual environment
4. **Install Dependencies**: Install PyInstaller, PyQt5, and PyYAML
5. **Verify Assets**: Check that required files exist (menu.py, config.yml, logos)
6. **Create PyInstaller Spec**: Generate a detailed build specification
7. **Build Executable**: Run PyInstaller to create the standalone executable
8. **Create Distribution Package**: Bundle executable with assets and documentation
9. **Create Archive**: Generate a ZIP file for easy distribution
10. **Cleanup**: Remove temporary build files

## Output

After a successful build, you'll get:

- **Distribution Directory**: `menu_YYYYMMDD_HHMMSS/`
  - `menu` (or `menu.exe` on Windows) - The standalone executable
  - `config.yml` - Current configuration
  - `config_sample.yml` - Sample configuration for reference
  - Asset files (logo.png, smallicon.png, greeting.sh if present)
  - `README.txt` - Instructions for end users
  - `run.sh` (Unix) or `run.bat` (Windows) - Convenience launcher

- **Compressed Archive**: `menu_YYYYMMDD_HHMMSS.zip`

## Customizing the Build

### Including Additional Assets

To include additional files in the executable package, modify the `data_files` list in the PyInstaller spec file creation section:

```python
data_files = [
    ('config.yml', '.'),
    ('logo.png', '.'),
    ('smallicon.png', '.'),
    ('my_custom_file.txt', '.'),  # Add your file here
]
```

### Changing the Executable Name

Modify the `name` parameter in the PyInstaller specification:

```python
exe = EXE(
    # ... other parameters ...
    name='my_custom_menu',  # Change this
    # ... rest of parameters ...
)
```

### Console vs. GUI Mode

The build creates a GUI application (no console window). To enable console output for debugging:

```python
exe = EXE(
    # ... other parameters ...
    console=True,  # Change to True for console mode
    # ... rest of parameters ...
)
```

## Troubleshooting

### Common Issues

1. **PyInstaller fails with import errors**:
   - Add missing modules to the `hiddenimports` list in the spec file
   - Check that all dependencies are installed in the build environment

2. **Assets not found at runtime**:
   - Verify files are listed in the `data_files` section
   - Check file paths are correct (relative to the script directory)

3. **Large executable size**:
   - PyInstaller bundles all dependencies, resulting in ~100-200MB executables
   - This is normal for PyQt5 applications

4. **Permission denied errors (Unix/Linux/macOS)**:
   - Make sure the build script is executable: `chmod +x build.sh`
   - Ensure you have write permissions in the build directory

5. **Antivirus false positives**:
   - Some antivirus software may flag PyInstaller executables
   - This is a known issue with packaged Python applications
   - Whitelist the executable or build directory if necessary

### Build Requirements

The build process requires these Python packages (automatically installed):

- `PyInstaller>=6.0.0` - Creates the standalone executable
- `PyQt5>=5.15.0` - GUI framework (must match your development version)
- `PyYAML>=6.0` - YAML configuration file parsing

### Platform-Specific Notes

**Windows**:
- Builds create `.exe` files
- May trigger Windows Defender SmartScreen on first run
- Include `run.bat` for easy launching

**macOS**:
- May require code signing for distribution
- Users might need to allow unsigned applications in Security preferences
- Executable will be larger due to Qt frameworks

**Linux**:
- Built executable should work on most Linux distributions
- May have issues with different glibc versions on very old systems
- Include `run.sh` for easy launching

## Distribution

To distribute your application:

1. **For single users**: Share the entire distribution directory
2. **For multiple users**: Share the ZIP archive
3. **For web distribution**: Upload the ZIP file to your website/GitHub releases

### End User Instructions

Include these instructions for your users:

1. Download and extract the ZIP file
2. Run the executable directly (no installation required)
3. Modify `config.yml` to customize the menu
4. Use `run.sh` (Unix) or `run.bat` (Windows) for convenience

The application will look for configuration files in this order:
1. Command line argument: `./menu my_config.yml`
2. Default: `config.yml` in the same directory as the executable

## Development vs. Production

**Development**: Use virtual environments and run `python menu.py`
**Production**: Use the built executable for end-user distribution

The build process creates completely self-contained applications that work without Python installations, making them ideal for distribution to non-technical users.
