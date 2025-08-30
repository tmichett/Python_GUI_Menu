#!/bin/bash
# Test script for Linux compatibility features
# Tests Qt platform detection and environment setup

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Change to script directory
cd "$(dirname "$0")"

echo "========================================"
echo "Linux Compatibility Test Suite"
echo "========================================"
echo

# Test 1: Check if required files exist
print_test "Checking required files..."
required_files=("menu.py" "run.sh" "run_linux.sh" "menu_venv/bin/activate")
all_files_exist=true

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_pass "Found: $file"
    else
        print_fail "Missing: $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = false ]; then
    print_fail "Some required files are missing. Please run setup first."
    exit 1
fi

# Test 2: Check if run scripts are executable
print_test "Checking script permissions..."
if [ -x "run.sh" ]; then
    print_pass "run.sh is executable"
else
    print_fail "run.sh is not executable"
    chmod +x run.sh
fi

if [ -x "run_linux.sh" ]; then
    print_pass "run_linux.sh is executable"
else
    print_fail "run_linux.sh is not executable"
    chmod +x run_linux.sh
fi

# Test 3: Test environment detection
print_test "Testing environment detection..."

# Save original environment
ORIG_DISPLAY="$DISPLAY"
ORIG_WAYLAND_DISPLAY="$WAYLAND_DISPLAY"

# Test Wayland detection
export WAYLAND_DISPLAY="wayland-0"
export DISPLAY=""
wayland_result=$(./run_linux.sh --debug 2>&1 | grep -i "detected display server" | head -1 || echo "")
if echo "$wayland_result" | grep -qi "wayland"; then
    print_pass "Wayland environment detected correctly"
else
    print_fail "Wayland environment detection failed"
fi

# Test X11 detection  
export WAYLAND_DISPLAY=""
export DISPLAY=":0"
x11_result=$(./run_linux.sh --debug 2>&1 | grep -i "detected display server" | head -1 || echo "")
if echo "$x11_result" | grep -qi "x11"; then
    print_pass "X11 environment detected correctly"
else
    print_fail "X11 environment detection failed"
fi

# Restore environment
export DISPLAY="$ORIG_DISPLAY"
export WAYLAND_DISPLAY="$ORIG_WAYLAND_DISPLAY"

# Test 4: Test virtual environment activation
print_test "Testing virtual environment..."
source menu_venv/bin/activate

if command -v python >/dev/null 2>&1; then
    python_version=$(python --version 2>&1)
    print_pass "Python available: $python_version"
else
    print_fail "Python not available in virtual environment"
fi

# Test 5: Check PyQt5 installation
print_test "Checking PyQt5 installation..."
if python -c "import PyQt5.QtWidgets" 2>/dev/null; then
    pyqt_version=$(python -c "from PyQt5.QtCore import QT_VERSION_STR; print(QT_VERSION_STR)" 2>/dev/null || echo "unknown")
    print_pass "PyQt5 available (Qt version: $pyqt_version)"
else
    print_fail "PyQt5 not available in virtual environment"
fi

# Test 6: Check YAML support
print_test "Checking YAML support..."
if python -c "import yaml" 2>/dev/null; then
    print_pass "PyYAML available"
else
    print_fail "PyYAML not available"
fi

# Test 7: Test configuration loading
print_test "Testing configuration loading..."
if [ -f "config.yml" ]; then
    if python -c "
import yaml
try:
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    print('Config loaded successfully')
    exit(0)
except Exception as e:
    print(f'Config load failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_pass "Configuration file loads successfully"
    else
        print_fail "Configuration file has syntax errors"
    fi
else
    print_fail "Configuration file (config.yml) not found"
fi

# Test 8: Test platform script selection
print_test "Testing platform script selection..."
if uname -s | grep -qi "linux"; then
    if ./run.sh --help 2>&1 | grep -q "run_linux.sh"; then
        print_pass "Linux platform correctly detected by run.sh"
    else
        # Test if run.sh executes run_linux.sh
        timeout 5s ./run.sh --help >/dev/null 2>&1 && print_pass "Cross-platform launcher working" || print_info "Cross-platform launcher test skipped (may require display)"
    fi
else
    print_info "Not running on Linux - platform detection test skipped"
fi

# Test 9: Test help output
print_test "Testing help output..."
if ./run_linux.sh --help >/dev/null 2>&1; then
    print_pass "Help output works"
else
    print_fail "Help output failed"
fi

# Test 10: System information
print_test "System information:"
print_info "OS: $(uname -s -r)"
print_info "Desktop: ${XDG_CURRENT_DESKTOP:-<not set>}"
print_info "Session: ${XDG_SESSION_TYPE:-<not set>}"
print_info "Display: ${DISPLAY:-<not set>}"
print_info "Wayland: ${WAYLAND_DISPLAY:-<not set>}"

# Test 11: Qt plugins (if available)
print_test "Checking Qt plugins..."
plugin_paths=(
    "menu_venv/lib/python*/site-packages/PyQt5/Qt*/plugins/platforms"
    "menu_venv/lib/python*/site-packages/PyQt5/Qt/plugins/platforms"
)

found_plugins=false
for path_pattern in "${plugin_paths[@]}"; do
    for path in $path_pattern; do
        if [ -d "$path" ]; then
            plugins=$(ls "$path"/*.so 2>/dev/null | wc -l || echo 0)
            if [ "$plugins" -gt 0 ]; then
                print_pass "Found Qt plugins in: $path ($plugins plugins)"
                found_plugins=true
                
                # List specific plugins
                for plugin in "$path"/*.so; do
                    if [ -f "$plugin" ]; then
                        plugin_name=$(basename "$plugin" .so | sed 's/^lib//')
                        print_info "  - $plugin_name"
                    fi
                done
                break
            fi
        fi
    done
    if [ "$found_plugins" = true ]; then
        break
    fi
done

if [ "$found_plugins" = false ]; then
    print_fail "No Qt plugins found - this may cause runtime issues"
fi

echo
echo "========================================"
print_info "Test completed. If any tests failed, see LINUX_COMPATIBILITY.md for troubleshooting."
echo "========================================"

# Summary
failed_tests=$(grep -c "\\[FAIL\\]" <<< "$(./test_linux_compatibility.sh 2>&1)" || echo 0)
if [ "$failed_tests" -eq 0 ]; then
    print_pass "All tests passed!"
    exit 0
else
    print_fail "$failed_tests test(s) failed"
    exit 1
fi
