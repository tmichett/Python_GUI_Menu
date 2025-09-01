#!/bin/bash
# RPM build script for Python GUI Menu Application
# This script prepares the application for RPM packaging

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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

# Get version from git tag or use default
get_version() {
    if git describe --tags --exact-match 2>/dev/null; then
        VERSION=$(git describe --tags --exact-match | sed 's/^v//')
    elif [ -n "$1" ]; then
        VERSION="$1"
    else
        VERSION="1.0.0"
    fi
    echo "$VERSION"
}

# Verify required files exist
verify_files() {
    print_status "Verifying required files..."
    
    local required_files=(
        "menu.py"
        "font_manager.py"
        "config.yml"
        "logo.png"
        "smallicon.png"
        "requirements_build.txt"
        "build.py"
    )
    
    local missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_error "Missing required files:"
        printf '  %s\n' "${missing_files[@]}"
        return 1
    fi
    
    print_success "All required files found"
    return 0
}

# Build the application using the existing build script
build_application() {
    print_status "Building application using Python build script..."
    
    # Clean any previous builds
    rm -rf build dist build_venv menu_* *.spec
    
    # Run the build script
    if ! python3 build.py; then
        print_error "Application build failed"
        return 1
    fi
    
    # Verify build output
    if [ ! -f "dist/menu" ]; then
        print_error "Build failed - executable not found in dist/"
        return 1
    fi
    
    # Find the package directory
    PACKAGE_DIR=$(ls -d menu_* 2>/dev/null | head -1)
    if [ -z "$PACKAGE_DIR" ]; then
        print_error "Package directory not found"
        return 1
    fi
    
    print_success "Application built successfully: $PACKAGE_DIR"
    echo "$PACKAGE_DIR"
}

# Prepare files for RPM packaging
prepare_rpm_files() {
    local package_dir="$1"
    local version="$2"
    
    print_status "Preparing files for RPM packaging..."
    
    # Create RPM build directories
    mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
    
    # Create source directory for packaging
    local source_dir="python-gui-menu-${version}"
    rm -rf "$source_dir"
    mkdir -p "$source_dir"
    
    # Copy application files
    cp -r "$package_dir"/* "$source_dir/"
    
    # Copy additional configuration and documentation
    cp config.yml "$source_dir/"
    cp -r Docs "$source_dir/" 2>/dev/null || print_warning "Docs directory not found"
    cp README.md "$source_dir/" 2>/dev/null || print_warning "README.md not found"
    cp python-gui-menu.desktop "$source_dir/" 2>/dev/null || print_warning "Desktop file not found"
    
    # Make sure executable has correct permissions
    chmod +x "$source_dir/menu"
    
    # Make scripts executable if they exist
    [ -f "$source_dir/run_linux.sh" ] && chmod +x "$source_dir/run_linux.sh"
    [ -f "$source_dir/greeting.sh" ] && chmod +x "$source_dir/greeting.sh"
    [ -f "$source_dir/run.sh" ] && chmod +x "$source_dir/run.sh"
    
    # Create tarball for RPM
    tar -czf ~/rpmbuild/SOURCES/python-gui-menu-${version}.tar.gz "$source_dir"
    
    print_success "RPM source files prepared"
    
    # Clean up temporary directory
    rm -rf "$source_dir"
}

# Create RPM spec file
create_spec_file() {
    local version="$1"
    
    print_status "Creating RPM spec file..."
    
    cat > ~/rpmbuild/SPECS/python-gui-menu.spec << EOF
Name:           python-gui-menu
Version:        ${version}
Release:        1%{?dist}
Summary:        Python GUI Menu Application

License:        MIT
URL:            https://github.com/your-repo/Python_GUI_Menu
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  desktop-file-utils
Requires:       qt5-qtbase-gui
Requires:       qt5-qtwayland
Requires:       libxcb
Requires:       fontconfig

%description
A cross-platform GUI menu application built with Python and PyQt5.
Provides a customizable menu interface for executing system commands
and managing system tasks through an intuitive graphical interface.

The application supports multi-column layouts, real-time command output,
help documentation system, and cross-platform compatibility.

%prep
%autosetup

%build
# No build needed - using pre-built executable

%install
# Create installation directories
mkdir -p %{buildroot}/opt/PythonMenu
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/pixmaps

# Install application files to /opt/PythonMenu
cp -r * %{buildroot}/opt/PythonMenu/

# Ensure executable has correct permissions
chmod +x %{buildroot}/opt/PythonMenu/menu

# Install scripts with correct permissions
if [ -f %{buildroot}/opt/PythonMenu/run_linux.sh ]; then
    chmod +x %{buildroot}/opt/PythonMenu/run_linux.sh
fi

if [ -f %{buildroot}/opt/PythonMenu/greeting.sh ]; then
    chmod +x %{buildroot}/opt/PythonMenu/greeting.sh
fi

if [ -f %{buildroot}/opt/PythonMenu/run.sh ]; then
    chmod +x %{buildroot}/opt/PythonMenu/run.sh
fi

# Create wrapper script in /usr/bin
cat > %{buildroot}/usr/bin/python-gui-menu << 'WRAPPER_EOF'
#!/bin/bash
# Wrapper script for Python GUI Menu
cd /opt/PythonMenu
exec ./menu "\$@"
WRAPPER_EOF
chmod +x %{buildroot}/usr/bin/python-gui-menu

# Install desktop entry
if [ -f python-gui-menu.desktop ]; then
    cp python-gui-menu.desktop %{buildroot}/usr/share/applications/
else
    cat > %{buildroot}/usr/share/applications/python-gui-menu.desktop << 'DESKTOP_EOF'
[Desktop Entry]
Name=Python GUI Menu
Comment=Customizable GUI menu application
Exec=/usr/bin/python-gui-menu
Icon=python-gui-menu
Terminal=false
Type=Application
Categories=Utility;System;
DESKTOP_EOF
fi

# Install icon
if [ -f logo.png ]; then
    cp logo.png %{buildroot}/usr/share/pixmaps/python-gui-menu.png
elif [ -f smallicon.png ]; then
    cp smallicon.png %{buildroot}/usr/share/pixmaps/python-gui-menu.png
fi

%check
# Validate desktop file
desktop-file-validate %{buildroot}/usr/share/applications/python-gui-menu.desktop

%files
/opt/PythonMenu/
/usr/bin/python-gui-menu
/usr/share/applications/python-gui-menu.desktop
%{_datadir}/pixmaps/python-gui-menu.png

%post
# Update desktop database
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications || :
fi

%postun
# Update desktop database
if [ -x /usr/bin/update-desktop-database ]; then
    /usr/bin/update-desktop-database -q /usr/share/applications || :
fi

%changelog
* $(date '+%a %b %d %Y') Build Script <build@localhost> - ${version}-1
- Initial RPM package
- Cross-platform enhanced build
- Installation in /opt/PythonMenu directory
- Desktop integration with menu entry and icon

EOF

    print_success "RPM spec file created"
}

# Build RPM package
build_rpm() {
    print_status "Building RPM package..."
    
    if ! rpmbuild -ba ~/rpmbuild/SPECS/python-gui-menu.spec; then
        print_error "RPM build failed"
        return 1
    fi
    
    # Find the generated RPM
    local rpm_file
    rpm_file=$(find ~/rpmbuild/RPMS -name "*.rpm" -type f | head -1)
    
    if [ -z "$rpm_file" ]; then
        print_error "RPM package not found"
        return 1
    fi
    
    # Copy to current directory
    cp "$rpm_file" ./
    local rpm_filename
    rpm_filename=$(basename "$rpm_file")
    
    print_success "RPM package built: $rpm_filename"
    
    # Show package info
    echo ""
    print_status "Package information:"
    rpm -qip "$rpm_filename"
    
    echo ""
    print_status "Package files:"
    rpm -qlp "$rpm_filename" | head -20
    
    echo "$rpm_filename"
}

# Main function
main() {
    print_status "Python GUI Menu - RPM Build Script"
    echo "======================================"
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Get version
    local version
    version=$(get_version "$1")
    print_status "Building version: $version"
    
    # Verify prerequisites
    if ! verify_files; then
        exit 1
    fi
    
    # Check if rpmbuild is available
    if ! command -v rpmbuild >/dev/null 2>&1; then
        print_error "rpmbuild not found. Install rpm-build package:"
        print_error "  dnf install rpm-build rpmdevtools"
        exit 1
    fi
    
    # Build application
    local package_dir
    if ! package_dir=$(build_application); then
        exit 1
    fi
    
    # Prepare RPM files
    if ! prepare_rpm_files "$package_dir" "$version"; then
        exit 1
    fi
    
    # Create spec file
    if ! create_spec_file "$version"; then
        exit 1
    fi
    
    # Build RPM
    local rpm_file
    if ! rpm_file=$(build_rpm); then
        exit 1
    fi
    
    print_success "Build completed successfully!"
    echo ""
    print_status "Generated files:"
    echo "  RPM Package: $rpm_file"
    echo "  Source: ~/rpmbuild/SOURCES/python-gui-menu-${version}.tar.gz"
    echo "  Spec File: ~/rpmbuild/SPECS/python-gui-menu.spec"
    echo ""
    print_status "To install the package:"
    echo "  sudo dnf install ./$rpm_file"
    echo ""
    print_status "To run the application after installation:"
    echo "  python-gui-menu"
    echo "  # or from the desktop menu: Python GUI Menu"
}

# Handle command line arguments
case "${1:-}" in
    "--help"|"-h")
        echo "Usage: $0 [version]"
        echo ""
        echo "Build RPM package for Python GUI Menu application."
        echo ""
        echo "Arguments:"
        echo "  version    Version string (default: auto-detect from git or 1.0.0)"
        echo ""
        echo "Examples:"
        echo "  $0              # Auto-detect version"
        echo "  $0 1.2.3        # Build specific version"
        echo ""
        echo "Requirements:"
        echo "  - rpm-build and rpmdevtools packages"
        echo "  - Python 3 with venv support"
        echo "  - All application source files"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
