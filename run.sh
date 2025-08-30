#!/bin/bash
# Cross-platform run script for Python GUI Menu
# Automatically detects the platform and uses appropriate Qt configuration

cd "$(dirname "$0")"

# Function to detect if we're running from binary or source
detect_runtime_mode() {
    if [ -f "menu" ] && [ -x "menu" ]; then
        echo "binary"
    elif [ -f "menu.py" ] && [ -d "menu_venv" ]; then
        echo "source"
    else
        echo "unknown"
    fi
}

# Detect operating system and runtime mode
OS=$(uname -s)
RUNTIME_MODE=$(detect_runtime_mode)

echo "Detected OS: $OS, Runtime: $RUNTIME_MODE"

case "$OS" in
    "Linux")
        # On Linux, use the enhanced launcher that handles Wayland/X11
        exec ./run_linux.sh "$@"
        ;;
    "Darwin")
        # macOS launcher - handle both binary and source
        case "$RUNTIME_MODE" in
            "binary")
                echo "Running macOS binary..."
                exec ./menu "$@"
                ;;
            "source")
                echo "Running macOS from source..."
                source menu_venv/bin/activate
                python menu.py "$@" &
                ;;
            *)
                echo "Error: Cannot determine runtime mode on macOS"
                echo "Need either 'menu' executable or 'menu.py' + 'menu_venv/'"
                ls -la
                exit 1
                ;;
        esac
        ;;
    *)
        # Other Unix-like systems
        echo "Detected OS: $OS - using basic launcher"
        case "$RUNTIME_MODE" in
            "binary")
                echo "Running binary executable..."
                exec ./menu "$@"
                ;;
            "source")
                echo "Running from Python source..."
                source menu_venv/bin/activate
                python menu.py "$@" &
                ;;
            *)
                echo "Error: Cannot determine runtime mode"
                echo "Need either 'menu' executable or 'menu.py' + 'menu_venv/'"
                ls -la
                exit 1
                ;;
        esac
        ;;
esac
