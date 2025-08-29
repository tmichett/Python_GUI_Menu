#!/bin/bash

# Build script for Python GUI Menu Application
# Creates a self-contained executable using PyInstaller

set -e  # Exit on any error

echo "================================================="
echo "Building Python GUI Menu Application"
echo "================================================="

# Configuration
APP_NAME="menu"
PYTHON_VERSION="3.12"
BUILD_DIR="build"
DIST_DIR="dist"
VENV_DIR="build_venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

if ! command_exists pip; then
    print_error "pip is not installed or not in PATH"
    exit 1
fi

print_success "Prerequisites check passed"

# Clean previous builds
print_status "Cleaning previous build artifacts..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "$VENV_DIR" *.spec
print_success "Cleaned previous builds"

# Create build virtual environment
print_status "Creating build virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
print_success "Build virtual environment created"

# Upgrade pip and install build dependencies
print_status "Installing build dependencies..."
pip install --upgrade pip
pip install pyinstaller PyQt5 PyYAML
print_success "Build dependencies installed"

# Verify required files exist
print_status "Verifying required files..."
required_files=("menu.py" "font_manager.py" "config.yml" "logo.png" "smallicon.png")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    print_error "Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi
print_success "All required files found"

# Create PyInstaller spec file for better control
print_status "Creating PyInstaller specification..."
cat > menu.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis

# Get the current directory
basedir = os.path.abspath('.')

# Define data files to include
data_files = [
    ('config.yml', '.'),
    ('logo.png', '.'),
    ('smallicon.png', '.'),
]

# Add greeting.sh if it exists
if os.path.exists('greeting.sh'):
    data_files.append(('greeting.sh', '.'))

# Add any other .png files in the root directory
for file in os.listdir('.'):
    if file.endswith('.png') and file not in ['logo.png', 'smallicon.png']:
        data_files.append((file, '.'))

a = Analysis(
    ['menu.py', 'font_manager.py'],
    pathex=[basedir],
    binaries=[],
    datas=data_files,
    hiddenimports=[
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='menu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='smallicon.png' if os.path.exists('smallicon.png') else None,
)
EOF
print_success "PyInstaller specification created"

# Run PyInstaller
print_status "Building executable with PyInstaller..."
pyinstaller menu.spec --clean --noconfirm

if [[ $? -eq 0 ]]; then
    print_success "PyInstaller build completed successfully"
else
    print_error "PyInstaller build failed"
    exit 1
fi

# Verify the executable was created
if [[ -f "dist/menu" ]]; then
    print_success "Executable created: dist/menu"
    
    # Make executable
    chmod +x dist/menu
    
    # Get file size
    file_size=$(du -h dist/menu | cut -f1)
    print_status "Executable size: $file_size"
else
    print_error "Executable not found in dist directory"
    exit 1
fi

# Create a distribution package
print_status "Creating distribution package..."
PACKAGE_NAME="${APP_NAME}_$(date +%Y%m%d_%H%M%S)"
PACKAGE_DIR="$PACKAGE_NAME"

mkdir -p "$PACKAGE_DIR"

# Copy executable
cp dist/menu "$PACKAGE_DIR/"

# Copy additional configuration files that users might want to modify
cp config.yml "$PACKAGE_DIR/config.yml"
cp logo.png "$PACKAGE_DIR/" 2>/dev/null || true
cp smallicon.png "$PACKAGE_DIR/" 2>/dev/null || true
cp greeting.sh "$PACKAGE_DIR/" 2>/dev/null || true

# Create a sample configuration
cat > "$PACKAGE_DIR/config_sample.yml" << 'EOF'
# Sample configuration for Python GUI Menu
# Copy this to config.yml and modify as needed

icon: smallicon.png
logo: logo.png
logo_size: 320x240
menu_title: My Custom Menu
menu_help: echo "This is a help message"
num_columns: 1

menu_items:
  - name: System Commands
    items:
      - name: List Directory
        command: ls -la
      - name: Current Date
        command: date
      - name: System Info
        command: uname -a
        
  - name: File Operations
    items:
      - name: Create Test File
        command: echo "Hello World" > test.txt
      - name: Show Test File
        command: cat test.txt
EOF

# Create README for distribution
cat > "$PACKAGE_DIR/README.txt" << EOF
Python GUI Menu Application
===========================

This is a self-contained executable of the Python GUI Menu application.
No Python installation or virtual environment is required to run this application.

Files in this package:
- menu: The main executable
- config.yml: Current configuration file
- config_sample.yml: Sample configuration for reference
- logo.png: Logo image (if present)
- smallicon.png: Window icon (if present)
- greeting.sh: Sample script (if present)

To run:
./menu

To use a different configuration file:
./menu my_custom_config.yml

To modify the menu:
1. Edit config.yml (or create a new YAML file)
2. Update the menu_items section with your commands
3. Run the executable

Configuration Format:
The application uses YAML configuration files. See config_sample.yml
for examples of the configuration format.

For more information, see: https://github.com/your-repo/Python_GUI_Menu
EOF

# Create run script for convenience
cat > "$PACKAGE_DIR/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./menu
EOF
chmod +x "$PACKAGE_DIR/run.sh"

print_success "Distribution package created: $PACKAGE_DIR"

# Create compressed archive
print_status "Creating compressed archive..."
if command_exists tar; then
    tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_DIR"
    archive_size=$(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)
    print_success "Archive created: ${PACKAGE_NAME}.tar.gz ($archive_size)"
else
    print_warning "tar not available, skipping archive creation"
fi

# Clean up build environment
print_status "Cleaning up build environment..."
deactivate 2>/dev/null || true
rm -rf "$VENV_DIR" "$BUILD_DIR" menu.spec
print_success "Build environment cleaned"

# Summary
echo ""
echo "================================================="
print_success "BUILD COMPLETED SUCCESSFULLY!"
echo "================================================="
echo ""
echo "Distribution package: $PACKAGE_DIR"
if [[ -f "${PACKAGE_NAME}.tar.gz" ]]; then
    echo "Compressed archive: ${PACKAGE_NAME}.tar.gz"
fi
echo ""
echo "To test the executable:"
echo "  cd $PACKAGE_DIR"
echo "  ./menu"
echo ""
echo "To distribute:"
echo "  Share the entire '$PACKAGE_DIR' directory or"
echo "  Share the '${PACKAGE_NAME}.tar.gz' archive"
echo ""
