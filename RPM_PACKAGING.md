# RPM Packaging for Python GUI Menu

This document describes how to build and install RPM packages for the Python GUI Menu application.

## Overview

The application can be packaged as an RPM for easy installation and distribution on Red Hat-based Linux systems (RHEL, CentOS, Fedora, etc.). The RPM package includes:

- Pre-built executable installed in `/opt/PythonMenu/`
- Desktop integration with menu entry and icon
- System wrapper script at `/usr/bin/python-gui-menu`
- All required configuration files and documentation

## Automated Build with GitHub Actions

### Triggering the Build

The automated RPM build is triggered by:

1. **Git Tags**: Push a version tag (e.g., `v1.0.0`)
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Manual Workflow**: Run from GitHub Actions tab
   - Go to your repository's "Actions" tab
   - Select "Build RPM Package" workflow
   - Click "Run workflow"
   - Optionally specify a release tag

### Build Process

The GitHub Action:

1. Uses CentOS Stream 9 container for authentic RPM environment
2. Installs all required dependencies (Qt5, Python, build tools)
3. Builds the application using cross-platform enhanced mode
4. Creates proper RPM package with all files
5. Tests the installation process
6. Uploads the RPM as an artifact
7. Creates a GitHub release (for tagged builds)

### Artifacts

After a successful build:
- RPM package is available as GitHub artifact
- For tagged builds: RPM is attached to the GitHub release
- Package name format: `python-gui-menu-<version>-1.<arch>.rpm`

## Manual Local Build

### Prerequisites

On CentOS/RHEL/Fedora systems, install required packages:

```bash
# For CentOS Stream 9 / RHEL 9+ / Fedora
sudo dnf install rpm-build rpmdevtools python3 python3-pip python3-devel \
                 qt5-qtbase-devel desktop-file-utils

# For CentOS/RHEL 8
sudo dnf install rpm-build rpmdevtools python3 python3-pip python3-devel \
                 qt5-qtbase-devel desktop-file-utils

# For older systems with yum
sudo yum install rpm-build rpmdevtools python3 python3-pip python3-devel \
                 qt5-qtbase-devel desktop-file-utils
```

### Building the RPM

Use the included build script:

```bash
# Auto-detect version from git tags
./build-rpm.sh

# Or specify a version
./build-rpm.sh 1.0.0
```

The script will:
1. Verify all required files are present
2. Build the application using the existing build system
3. Prepare files for RPM packaging
4. Create the RPM spec file
5. Build the final RPM package

### Build Output

After successful build:
- RPM package: `python-gui-menu-<version>-1.<arch>.rpm`
- Source tarball: `~/rpmbuild/SOURCES/python-gui-menu-<version>.tar.gz`
- Spec file: `~/rpmbuild/SPECS/python-gui-menu.spec`

## Installation

### From RPM Package

```bash
# Install the RPM package
sudo dnf install ./python-gui-menu-*.rpm

# Or using rpm directly
sudo rpm -ivh python-gui-menu-*.rpm
```

### Verification

After installation, verify the package:

```bash
# Check installed files
rpm -ql python-gui-menu

# Check package information
rpm -qi python-gui-menu

# Test the application
python-gui-menu --help
```

## Package Contents

The RPM installs the following files:

### Application Files (`/opt/PythonMenu/`)
- `menu` - Main executable
- `config.yml` - Default configuration
- `config_sample.yml` - Sample configuration
- `logo.png`, `smallicon.png` - Application images  
- `run_linux.sh` - Enhanced Linux launcher script
- `Docs/` - Help documentation
- `README.txt` - Package documentation

### System Integration
- `/usr/bin/python-gui-menu` - System wrapper script
- `/usr/share/applications/python-gui-menu.desktop` - Desktop entry
- `/usr/share/pixmaps/python-gui-menu.png` - Application icon

## Usage After Installation

### Command Line
```bash
# Run with default configuration
python-gui-menu

# Run with custom configuration
python-gui-menu /path/to/custom_config.yml

# Run from installation directory
cd /opt/PythonMenu
./menu
```

### Desktop Environment
- Application appears in system menu under "Utilities" or "System"
- Can be launched from desktop environment's application launcher
- Search for "Python GUI Menu"

### Configuration

The application looks for configuration files in this order:
1. Command line argument: `python-gui-menu custom_config.yml`
2. Default configuration: `/opt/PythonMenu/config.yml`

To customize:
1. Copy `/opt/PythonMenu/config_sample.yml` to a new file
2. Edit the configuration as needed
3. Run with: `python-gui-menu /path/to/your_config.yml`

## Uninstalling

```bash
# Remove the package
sudo dnf remove python-gui-menu

# Or using rpm
sudo rpm -e python-gui-menu
```

This removes all installed files and cleans up desktop integration.

## Dependencies

### Build Dependencies
- `python3`, `python3-pip`, `python3-devel`
- `qt5-qtbase-devel` 
- `rpm-build`, `rpmdevtools`
- `desktop-file-utils`
- `gcc`, `gcc-c++`, `make` (for PyInstaller)

### Runtime Dependencies
- `qt5-qtbase-gui` - Qt5 GUI libraries
- `qt5-qtwayland` - Wayland support
- `libxcb` - X11 connection library
- `fontconfig` - Font configuration

All runtime dependencies are automatically installed with the RPM.

## Troubleshooting

### Build Issues

1. **"rpmbuild not found"**
   ```bash
   sudo dnf install rpm-build rpmdevtools
   ```

2. **"No match for argument: python3-venv"**
   - In CentOS Stream 9, `venv` is included in the base `python3` package
   - Use `python3-devel` instead for development headers
   ```bash
   sudo dnf install python3-devel
   ```

3. **"PyQt5 installation failed"**
   ```bash
   sudo dnf install qt5-qtbase-devel python3-devel gcc gcc-c++
   ```

4. **"Desktop file validation failed"**
   ```bash
   sudo dnf install desktop-file-utils
   ```

### Runtime Issues

1. **"Cannot find Qt platform plugin"**
   ```bash
   sudo dnf install qt5-qtbase-gui qt5-qtwayland
   ```

2. **Application won't start**
   - Run with debug: `cd /opt/PythonMenu && ./run_linux.sh --debug`
   - Check dependencies: `ldd /opt/PythonMenu/menu`

3. **Missing desktop entry**
   - Reinstall package: `sudo dnf reinstall python-gui-menu`
   - Update desktop database: `sudo update-desktop-database`

## Advanced Usage

### Custom Packaging

To create a customized RPM:

1. Modify the spec file template in `build-rpm.sh`
2. Add additional files or dependencies
3. Rebuild: `./build-rpm.sh`

### Integration with CI/CD

The GitHub Action can be integrated into larger CI/CD workflows:

```yaml
- name: Build RPM
  uses: ./.github/workflows/build-rpm.yml
  
- name: Deploy to Repository
  run: |
    # Upload to your RPM repository
    scp *.rpm user@repo-server:/path/to/repo/
    # Update repository metadata
    ssh user@repo-server "cd /path/to/repo && createrepo ."
```

## Support

For issues with:
- **Application functionality**: Check main project README
- **RPM packaging**: Review this document and GitHub Action logs
- **Installation issues**: Check system logs and dependency requirements

The automated GitHub Action provides the most reliable build environment and should be preferred for production use.
