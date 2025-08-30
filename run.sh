#!/bin/bash
# Cross-platform run script for Python GUI Menu
# Automatically detects the platform and uses appropriate Qt configuration

cd "$(dirname "$0")"

# Detect operating system
OS=$(uname -s)

case "$OS" in
    "Linux")
        # On Linux, use the enhanced launcher that handles Wayland/X11
        exec ./run_linux.sh "$@"
        ;;
    "Darwin")
        # macOS - use simple launcher
        source menu_venv/bin/activate
        python menu.py "$@" &
        ;;
    *)
        # Other Unix-like systems - basic launcher
        echo "Detected OS: $OS - using basic launcher"
        source menu_venv/bin/activate
        python menu.py "$@" &
        ;;
esac
