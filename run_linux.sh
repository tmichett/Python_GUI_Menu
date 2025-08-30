#!/bin/bash
# Enhanced run script for Python GUI Menu with cross-platform Qt support
# Handles X11, Wayland, and fallback scenarios on Linux systems

# Function to print status messages
print_status() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Change to script directory
cd "$(dirname "$0")"

# Function to detect display server
detect_display_server() {
    if [ -n "$WAYLAND_DISPLAY" ]; then
        echo "wayland"
    elif [ -n "$DISPLAY" ]; then
        echo "x11"
    else
        echo "unknown"
    fi
}

# Function to check if a Qt platform plugin is available
check_qt_plugin() {
    local plugin=$1
    # Try to find the plugin in common locations
    local plugin_paths=(
        "menu_venv/lib/python*/site-packages/PyQt5/Qt5/plugins/platforms"
        "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms"
        "/usr/lib64/qt5/plugins/platforms"
        "/usr/local/lib/qt5/plugins/platforms"
    )
    
    for path in "${plugin_paths[@]}"; do
        if ls $path/lib${plugin}.so 2>/dev/null | head -1 > /dev/null; then
            return 0
        fi
    done
    return 1
}

# Function to set Qt environment variables
setup_qt_environment() {
    local display_server=$(detect_display_server)
    print_status "Detected display server: $display_server"
    
    # Clear any existing Qt platform settings
    unset QT_QPA_PLATFORM
    unset QT_QPA_PLATFORM_PLUGIN_PATH
    
    case $display_server in
        "wayland")
            print_status "Setting up Qt for Wayland environment"
            
            # Try different Wayland platform options in order of preference
            local wayland_plugins=("wayland" "wayland-egl" "wayland-xcomposite-egl")
            
            for plugin in "${wayland_plugins[@]}"; do
                if check_qt_plugin "$plugin"; then
                    export QT_QPA_PLATFORM="$plugin"
                    print_success "Using Qt platform plugin: $plugin"
                    break
                fi
            done
            
            # If no Wayland plugin found, try xcb as fallback
            if [ -z "$QT_QPA_PLATFORM" ]; then
                print_warning "No Wayland plugins found, trying xcb fallback"
                if check_qt_plugin "xcb"; then
                    export QT_QPA_PLATFORM="xcb"
                    print_success "Using Qt platform plugin: xcb (fallback)"
                fi
            fi
            
            # Wayland-specific environment variables
            export QT_AUTO_SCREEN_SCALE_FACTOR=1
            export QT_WAYLAND_DISABLE_WINDOWDECORATION=0
            ;;
            
        "x11")
            print_status "Setting up Qt for X11 environment"
            
            if check_qt_plugin "xcb"; then
                export QT_QPA_PLATFORM="xcb"
                print_success "Using Qt platform plugin: xcb"
            fi
            ;;
            
        *)
            print_warning "Unknown display server, using Qt auto-detection"
            # Let Qt choose the best available platform
            ;;
    esac
    
    # Additional Qt environment variables for better compatibility
    export QT_X11_NO_MITSHM=1  # Disable shared memory extension (can cause issues)
    export QT_LOGGING_RULES="qt.qpa.plugin=false"  # Reduce Qt plugin logging
    
    # Font rendering improvements
    export QT_AUTO_SCREEN_SCALE_FACTOR=1
    export QT_SCALE_FACTOR_ROUNDING_POLICY=RoundPreferFloor
}

# Function to install missing system dependencies (if running as root/sudo)
install_qt_dependencies() {
    print_status "Checking Qt platform dependencies..."
    
    # Detect package manager
    if command -v dnf >/dev/null 2>&1; then
        PKG_MANAGER="dnf"
        QT_PACKAGES="qt5-qtbase-gui qt5-qtwayland"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MANAGER="yum"
        QT_PACKAGES="qt5-qtbase-gui qt5-qtwayland"
    elif command -v apt >/dev/null 2>&1; then
        PKG_MANAGER="apt"
        QT_PACKAGES="libqt5gui5 qtwayland5"
    elif command -v pacman >/dev/null 2>&1; then
        PKG_MANAGER="pacman"
        QT_PACKAGES="qt5-base qt5-wayland"
    else
        print_warning "Unknown package manager - cannot auto-install dependencies"
        return 1
    fi
    
    # Check if we can install packages (root/sudo)
    if [ "$EUID" -eq 0 ] || sudo -n true 2>/dev/null; then
        print_status "Installing Qt dependencies with $PKG_MANAGER..."
        case $PKG_MANAGER in
            "dnf"|"yum")
                sudo $PKG_MANAGER install -y $QT_PACKAGES
                ;;
            "apt")
                sudo apt update && sudo apt install -y $QT_PACKAGES
                ;;
            "pacman")
                sudo pacman -S --noconfirm $QT_PACKAGES
                ;;
        esac
    else
        print_warning "Cannot install system dependencies (no root/sudo access)"
        print_warning "Please install these packages manually: $QT_PACKAGES"
    fi
}

# Function to run with diagnostic information
run_with_diagnostics() {
    print_status "Qt Environment Variables:"
    env | grep -E "^QT_|^DISPLAY|^WAYLAND" | sort
    
    print_status "Available Qt plugins:"
    find menu_venv/lib/python*/site-packages/PyQt5/Qt5/plugins/platforms -name "*.so" 2>/dev/null | xargs basename -s .so | sed 's/lib//' | sort || echo "  (Could not list plugins)"
    
    print_status "Display server information:"
    echo "  DISPLAY: ${DISPLAY:-<not set>}"
    echo "  WAYLAND_DISPLAY: ${WAYLAND_DISPLAY:-<not set>}"
    echo "  XDG_SESSION_TYPE: ${XDG_SESSION_TYPE:-<not set>}"
    
    print_status "System information:"
    echo "  OS: $(lsb_release -d 2>/dev/null | cut -f2 || echo "$(uname -s) $(uname -r)")"
    echo "  Desktop: ${XDG_CURRENT_DESKTOP:-<not set>}"
    
    echo "----------------------------------------"
    print_status "Starting application..."
}

# Main execution
main() {
    print_status "Python GUI Menu - Linux Compatibility Launcher"
    print_status "Checking virtual environment..."
    
    # Check if virtual environment exists
    if [ ! -d "menu_venv" ]; then
        print_error "Virtual environment not found. Please run the setup first."
        exit 1
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source menu_venv/bin/activate
    
    # Check if Python application exists
    if [ ! -f "menu.py" ]; then
        print_error "menu.py not found in current directory"
        exit 1
    fi
    
    # Setup Qt environment
    setup_qt_environment
    
    # Check if we need to show diagnostics
    if [ "$1" = "--debug" ] || [ "$1" = "-d" ]; then
        run_with_diagnostics
    fi
    
    # Try to run the application
    print_status "Launching Python GUI Menu..."
    
    # First attempt with current settings
    if python menu.py "${@}" 2>/dev/null; then
        print_success "Application started successfully"
        exit 0
    fi
    
    # If first attempt failed, show diagnostics and try alternatives
    print_warning "Initial launch failed, trying alternative configurations..."
    
    # Try with minimal platform (as last resort)
    export QT_QPA_PLATFORM="minimal"
    print_status "Trying minimal platform (headless mode)..."
    if python menu.py "${@}" 2>/dev/null; then
        print_success "Application started with minimal platform"
        exit 0
    fi
    
    # If all else fails, show detailed error information
    print_error "Failed to start the application. Running with full error output:"
    echo "----------------------------------------"
    
    # Reset to auto-detection and show full errors
    unset QT_QPA_PLATFORM
    python menu.py "${@}"
    
    echo "----------------------------------------"
    print_error "Application failed to start."
    print_status "Troubleshooting suggestions:"
    echo "  1. Try: $0 --debug    (for diagnostic information)"
    echo "  2. Install Qt dependencies: sudo dnf install qt5-qtbase-gui qt5-qtwayland"
    echo "  3. Try running in X11 mode: WAYLAND_DISPLAY= $0"
    echo "  4. Check PyQt5 installation: pip list | grep PyQt"
    
    exit 1
}

# Handle command line arguments
case "$1" in
    "--help"|"-h")
        echo "Usage: $0 [options] [config_file]"
        echo ""
        echo "Options:"
        echo "  --debug, -d    Show diagnostic information"
        echo "  --help, -h     Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0                           # Run with default config"
        echo "  $0 custom_config.yml         # Run with custom config"
        echo "  $0 --debug                   # Run with diagnostic output"
        echo ""
        exit 0
        ;;
    "--install-deps")
        install_qt_dependencies
        exit $?
        ;;
    *)
        main "$@"
        ;;
esac
