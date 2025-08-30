#!/bin/bash
# Simple build menu to choose between Python and Bash build scripts

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Python GUI Menu - Build Options"
echo "========================================"
echo

echo -e "${BLUE}Choose your build method:${NC}"
echo "1. Bash build script (build.sh) - Proven, reliable"
echo "2. Python build script (build.py) - Cross-platform, enhanced"  
echo "3. Quick bash build (no packages)"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}Using Bash build script...${NC}"
        exec ./build.sh
        ;;
    2)
        echo -e "${GREEN}Using Python build script...${NC}"
        exec python build.py
        ;;
    3)
        echo -e "${GREEN}Running quick bash build...${NC}"
        echo "This will build without creating a distribution package"
        
        # Quick build steps
        echo "Cleaning previous builds..."
        rm -rf build dist build_venv *.spec
        
        echo "Creating build environment..."
        python3 -m venv build_venv
        source build_venv/bin/activate
        
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install pyinstaller PyQt5 PyYAML
        
        echo "Building executable..."
        pyinstaller --onefile --windowed --add-data "config.yml:." --add-data "logo.png:." --add-data "smallicon.png:." --icon="smallicon.png" menu.py
        
        echo "Build complete! Executable is in dist/menu"
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Invalid choice. Please run again and select 1-4.${NC}"
        exit 1
        ;;
esac
