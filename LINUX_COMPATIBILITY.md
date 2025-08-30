# Linux Compatibility Guide

## Overview

This guide addresses Qt platform plugin issues when running the Python GUI Menu application on Linux systems, particularly with Wayland display servers like those found on RHEL 8+, Fedora, and Ubuntu 22.04+.

## The Problem

When running PyQt5 applications on Linux systems with Wayland, you might encounter this error:

```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized.
```

This happens because:
1. Qt is trying to use the X11 (xcb) plugin on a Wayland system
2. The xcb plugin may be missing dependencies
3. Qt doesn't automatically detect and use appropriate Wayland plugins

## The Solution

We've created an enhanced Linux launcher (`run_linux.sh`) that:

1. **Detects your display server** (Wayland vs X11)
2. **Sets appropriate Qt environment variables**
3. **Provides multiple fallback options**
4. **Includes diagnostic tools for troubleshooting**

## Usage

### Basic Usage

```bash
# Use the cross-platform launcher (recommended)
./run.sh

# Or use the Linux-specific launcher directly
./run_linux.sh
```

### Advanced Usage

```bash
# Show diagnostic information
./run_linux.sh --debug

# Use custom config file
./run_linux.sh custom_config.yml

# Show help
./run_linux.sh --help
```

## Environment Detection

The enhanced launcher automatically detects your environment:

### Wayland Detection
- Checks for `WAYLAND_DISPLAY` environment variable
- Uses Wayland-compatible Qt plugins: `wayland`, `wayland-egl`, `wayland-xcomposite-egl`
- Sets Wayland-specific Qt options

### X11 Detection  
- Checks for `DISPLAY` environment variable
- Uses X11-compatible Qt plugin: `xcb`
- Sets X11-specific Qt options

### Fallback Options
- If primary plugins fail, tries alternative plugins
- Includes minimal platform as last resort for headless testing
- Provides detailed error diagnostics

## System Dependencies

The application may require additional system packages:

### RHEL/CentOS/Fedora
```bash
# Install Qt5 dependencies
sudo dnf install qt5-qtbase-gui qt5-qtwayland

# Or with the launcher
./run_linux.sh --install-deps
```

### Ubuntu/Debian
```bash
# Install Qt5 dependencies
sudo apt install libqt5gui5 qtwayland5
```

### Arch Linux
```bash
# Install Qt5 dependencies
sudo pacman -S qt5-base qt5-wayland
```

## Environment Variables Used

The enhanced launcher sets several Qt environment variables:

### Platform Selection
- `QT_QPA_PLATFORM`: Specifies the Qt platform plugin to use
  - `wayland`: Native Wayland support
  - `wayland-egl`: Wayland with EGL backend
  - `xcb`: X11 support
  - `minimal`: Headless mode (diagnostic only)

### Compatibility Options  
- `QT_X11_NO_MITSHM=1`: Disables shared memory extension
- `QT_AUTO_SCREEN_SCALE_FACTOR=1`: Enables automatic scaling
- `QT_LOGGING_RULES="qt.qpa.plugin=false"`: Reduces Qt plugin logging
- `QT_WAYLAND_DISABLE_WINDOWDECORATION=0`: Enables window decorations on Wayland

## Troubleshooting

### Common Issues and Solutions

1. **"Could not load the Qt platform plugin 'xcb'"**
   - Use the enhanced launcher: `./run_linux.sh`
   - Install missing dependencies: `./run_linux.sh --install-deps`

2. **Application appears but is unresponsive on Wayland**
   - Try forcing X11 mode: `WAYLAND_DISPLAY= ./run_linux.sh`
   - Check if your desktop supports XWayland

3. **Font rendering issues**
   - The launcher sets font-related Qt variables automatically
   - Check if your system has the required font packages

4. **Application crashes immediately**
   - Run with debug mode: `./run_linux.sh --debug`
   - Check the diagnostic output for missing dependencies

### Manual Environment Override

You can manually override the platform detection:

```bash
# Force Wayland
QT_QPA_PLATFORM=wayland ./run_linux.sh

# Force X11  
QT_QPA_PLATFORM=xcb ./run_linux.sh

# Force minimal (diagnostic)
QT_QPA_PLATFORM=minimal ./run_linux.sh
```

## Development Environment Setup

If you're setting up the development environment on Linux:

1. **Create virtual environment:**
   ```bash
   python3 -m venv menu_venv
   source menu_venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install PyQt5 PyYAML
   ```

3. **Install system dependencies:**
   ```bash
   # RHEL/Fedora
   sudo dnf install qt5-qtbase-gui qt5-qtwayland python3-devel

   # Ubuntu/Debian  
   sudo apt install libqt5gui5 qtwayland5 python3-dev
   ```

4. **Test the application:**
   ```bash
   ./run_linux.sh --debug
   ```

## Building for Linux

When building the standalone executable for Linux:

1. The build process will include the enhanced launcher
2. The standalone executable handles platform detection internally
3. No additional Qt dependencies are needed for the executable

```bash
# Build the executable
python build.py

# The resulting package includes both run.sh and run_linux.sh
```

## Platform Compatibility Matrix

| OS/Desktop | Wayland | X11 | Notes |
|------------|---------|-----|-------|
| RHEL 8+ | ✅ | ✅ | Default Wayland, XWayland available |
| Fedora 35+ | ✅ | ✅ | Default Wayland, XWayland available |
| Ubuntu 22.04+ | ✅ | ✅ | Default Wayland, X11 option in login |
| CentOS Stream | ✅ | ✅ | Similar to RHEL |
| openSUSE | ✅ | ✅ | Wayland default on recent versions |
| Arch Linux | ✅ | ✅ | Depends on desktop environment |

## Additional Resources

- [Qt Platform Abstraction Documentation](https://doc.qt.io/qt-5/qpa.html)
- [Wayland Support in Qt](https://doc.qt.io/qt-5/wayland-and-qt.html)
- [PyQt5 Platform Issues](https://www.riverbankcomputing.com/software/pyqt/)

## Contributing

If you encounter issues on specific Linux distributions:

1. Run `./run_linux.sh --debug` and capture the output
2. Include your distribution details: `cat /etc/os-release`
3. Include desktop environment: `echo $XDG_CURRENT_DESKTOP`
4. Submit an issue with the diagnostic information

---

*Last updated: $(date)*
