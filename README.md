# Python_GUI_Menu

A powerful, configurable GUI menu application with an integrated help system. Create dynamic menus using YAML configuration files and provide comprehensive documentation through the built-in markdown help system.

## Key Features

- 🚀 **Dynamic Menu Creation**: Configure menus through YAML files
- 📚 **Integrated Help System**: Built-in markdown documentation with graphics support
- 🖥️ **Real-time Command Execution**: Live output streaming with interactive terminal
- 📱 **Multi-column Layouts**: Organize menu items in customizable column layouts
- 🎨 **Customizable Interface**: Logos, icons, tooltips, and styling options
- 📦 **Self-contained Builds**: Create standalone executables with PyInstaller
- 🐧 **Cross-platform**: Works on Linux (X11/Wayland), macOS, and Windows

## Basic Configuration Example

````yaml
icon: smallicon.png
logo: logo.png
logo_size: 320x240
menu_title: "My Application Menu"
num_columns: 2  # Multi-column layout

menu_items:
  - name: "System Commands"
    column: 1
    button_info: "System administration tasks"
    items:
      - name: "System Information"
        command: "uname -a"
        button_info: "Display system information"
      - name: "Disk Usage"
        command: "df -h"
        
  - name: "File Operations"
    column: 2
    submenu_columns: 2  # Submenu in 2 columns
    items:
      - name: "List Directory"
        column: 1
        command: "ls -alF"
      - name: "Current Path"
        column: 2
        command: "pwd"
````


![](20250423172157.png)

![](20250423172429.png)

## Integrated Help System

The application features a comprehensive help system with markdown rendering, graphics support, and configurable documentation.

### Help System Features

- **📖 Markdown Rendering**: Full markdown support with syntax highlighting, tables, and formatting
- **🖼️ Graphics Support**: Display images and graphics inline with documentation
- **🔗 Link Navigation**: External links open in browser, internal document navigation
- **📑 Table of Contents**: Automatic navigation between help topics
- **⚙️ Configurable**: Define help documents and topics through `help_config.yml`

### Help Configuration

Create a `Docs/help_config.yml` file to configure the help system:

```yaml
---
help_config: README.md          # Default help document
help_graphic: ../logo.png       # Help system graphic
help_topics:                    # Additional help topics
  - topic: "User Guide"
    document: "Docs/user-guide.md"
  - topic: "Troubleshooting"
    document: "Docs/troubleshooting.md"
  - topic: "Configuration Examples"
    document: "Docs/examples.md"
```

### Help Directory Structure

```
project/
├── menu.py                     # Main application
├── config.yml                  # Menu configuration
├── Docs/                       # Help system (external)
│   ├── help_config.yml         # Help configuration
│   ├── README.md               # Main help document
│   ├── user-guide.md           # Additional help topics
│   ├── troubleshooting.md      # More help content
│   └── images/                 # Help graphics
└── logo.png                    # Application logo
```

### Accessing Help

1. **Click Help Button**: Located in the top-right corner of the main window
2. **Browse Topics**: Use the table of contents panel to navigate
3. **View Content**: Rich markdown content with proper formatting
4. **Follow Links**: Click links to open external resources or navigate documents

The help system automatically detects and loads documentation from the `Docs/` directory, making it easy to maintain comprehensive user documentation alongside your application.

## Development Setup

### Creating the Virtual Environment and Running the Menu

````bash
uv venv menu_venv --python=3.12
source menu_venv/bin/activate
uv pip install PyQt5 PyYaml markdown
python menu.py
````

### Dependencies

For development, you need:
- **PyQt5**: GUI framework
- **PyYAML**: Configuration file parsing  
- **markdown**: Help system rendering (for integrated documentation)

## Building Standalone Executables

Create self-contained executables that don't require Python or virtual environments on the target system.

### Quick Build Options

````bash
# Interactive build menu (recommended for first-time users)
./build_menu.sh

# Or choose your preferred method:
./build.sh       # Bash script - proven, reliable (Linux/macOS)
python build.py  # Python script - cross-platform, enhanced
build.bat        # Windows batch script
````

**Which build method should I use?**
- **`./build_menu.sh`** - Interactive menu, great for first time
- **`./build.sh`** - If you prefer the proven bash approach (Linux/macOS)
- **`python build.py`** - If you want cross-platform compatibility

### Build Output

After building, you'll get:
- **Standalone executable**: No Python installation required
- **Distribution package**: Includes executable, config files, and assets
- **ZIP archive**: Ready for distribution

### Build Requirements

The build process automatically installs these dependencies:
- **PyInstaller**: Creates standalone executables
- **PyQt5**: GUI framework
- **PyYAML**: Configuration parsing
- **markdown**: Help system rendering with full markdown support

### For End Users

Once built, users receive a complete package containing:
- **Standalone executable** (no Python installation needed)
- **Configuration files** (`config.yml`, sample configs)
- **Help documentation** (`Docs/` directory with full help system)
- **Assets** (logos, icons, scripts)
- **README and run scripts** for easy setup

Users can:
1. Download and extract the distribution package
2. Run the executable directly (no installation needed) 
3. Customize menus by editing `config.yml`
4. Access comprehensive help through the built-in Help button
5. Modify help documentation by editing markdown files in `Docs/`

**No Python installation required on the target system!**

## Linux Compatibility

This application now includes enhanced Linux support for both **X11** and **Wayland** display servers:

### Quick Start on Linux
```bash
# Cross-platform launcher (automatically detects environment)
./run.sh

# Linux-specific launcher with diagnostics
./run_linux.sh --debug
```

### Supported Linux Distributions
- ✅ RHEL 8+ (including Wayland)
- ✅ Fedora 35+ (including Wayland) 
- ✅ Ubuntu 22.04+ (including Wayland)
- ✅ CentOS Stream
- ✅ openSUSE
- ✅ Arch Linux

### Common Issues Fixed
- **Qt platform plugin errors** on Wayland systems
- **"Could not load the Qt platform plugin 'xcb'"** errors
- **Font rendering issues** on Linux
- **Cross-platform compatibility** between macOS and Linux

See **[LINUX_COMPATIBILITY.md](LINUX_COMPATIBILITY.md)** for detailed troubleshooting.

## Documentation

### Technical Documentation
- **[BUILD.md](BUILD.md)**: Detailed build instructions and troubleshooting
- **[FONT_FIX.md](FONT_FIX.md)**: Font management system and Qt warning fixes  
- **[LINUX_COMPATIBILITY.md](LINUX_COMPATIBILITY.md)**: Linux and Wayland compatibility guide
- **[config.yml](config.yml)**: Current configuration example

### Help System Documentation  
- **[Docs/README.md](Docs/README.md)**: Comprehensive user guide and help system overview
- **[Docs/help_config.yml](Docs/help_config.yml)**: Help system configuration
- **Additional Topics**: See `Docs/` directory for complete help documentation

### Configuration Examples
- **Multi-column layouts** with customizable menu organization
- **Interactive help system** with markdown rendering
- **Cross-platform compatibility** settings
- **Advanced command execution** with real-time output

The integrated help system provides comprehensive documentation accessible directly from the application through the Help button.