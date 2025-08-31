#!/usr/bin/env python3
"""
Build script for Python GUI Menu Application
Creates a self-contained executable using PyInstaller
Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import sys
import shutil
import subprocess
import platform
import datetime
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @classmethod
    def disable_on_windows(cls):
        """Disable colors on Windows if not supported"""
        if platform.system() == 'Windows':
            cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = cls.NC = ''

def print_status(message):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def run_command(cmd, check=True, capture_output=False, timeout=300):
    """Run a command and handle errors"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip()
        else:
            print_status(f"Running: {cmd}")
            result = subprocess.run(cmd, shell=True, check=check, timeout=timeout)
            return True
    except subprocess.TimeoutExpired:
        print_error(f"Command timed out after {timeout}s: {cmd}")
        return None if capture_output else False
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {cmd}")
        if hasattr(e, 'stderr') and e.stderr:
            print_error(f"Error: {e.stderr}")
        elif hasattr(e, 'output') and e.output:
            print_error(f"Output: {e.output}")
        return None if capture_output else False

def check_prerequisites():
    """Check if required tools are installed"""
    print_status("Checking prerequisites...")
    
    # Check Python
    try:
        python_version = run_command("python --version", capture_output=True)
        if not python_version:
            python_version = run_command("python3 --version", capture_output=True)
            if not python_version:
                raise Exception("Python not found")
        print_status(f"Found {python_version}")
    except:
        print_error("Python 3 is not installed or not in PATH")
        return False
    
    # Check pip
    try:
        pip_version = run_command("pip --version", capture_output=True)
        if not pip_version:
            pip_version = run_command("pip3 --version", capture_output=True)
            if not pip_version:
                raise Exception("pip not found")
        print_status(f"Found pip")
    except:
        print_error("pip is not installed or not in PATH")
        return False
    
    print_success("Prerequisites check passed")
    return True

def clean_build():
    """Clean previous build artifacts"""
    print_status("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', 'build_venv', '__pycache__']
    files_to_clean = ['menu.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
    
    print_success("Cleaned previous builds")

def create_venv():
    """Create build virtual environment"""
    print_status("Creating build virtual environment...")
    
    # Try python3 first, then python
    python_cmd = "python3" if shutil.which("python3") else "python"
    
    print_status(f"Using Python command: {python_cmd}")
    
    # Create virtual environment with verbose output for debugging
    cmd = f"{python_cmd} -m venv build_venv"
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True, timeout=60)
        print_success("Build virtual environment created")
        return True
    except subprocess.TimeoutExpired:
        print_error("Virtual environment creation timed out (60s)")
        return False
    except subprocess.CalledProcessError as e:
        print_error(f"Virtual environment creation failed: {e}")
        if e.stderr:
            print_error(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print_error(f"Unexpected error creating virtual environment: {e}")
        return False

def get_venv_python():
    """Get the path to the virtual environment Python"""
    if platform.system() == 'Windows':
        return os.path.join('build_venv', 'Scripts', 'python.exe')
    else:
        return os.path.join('build_venv', 'bin', 'python')

def install_dependencies():
    """Install build dependencies"""
    print_status("Installing build dependencies...")
    
    venv_python = get_venv_python()
    
    # Check if the virtual environment python exists
    if not os.path.exists(venv_python):
        print_error(f"Virtual environment Python not found: {venv_python}")
        return False
    
    print_status(f"Using virtual environment Python: {venv_python}")
    
    # Upgrade pip with timeout
    print_status("Upgrading pip...")
    if not run_command(f'"{venv_python}" -m pip install --upgrade pip'):
        print_warning("pip upgrade failed, continuing anyway...")
    
    # Install requirements directly (not from file to avoid missing file issues)
    print_status("Installing PyInstaller...")
    if not run_command(f'"{venv_python}" -m pip install "PyInstaller>=6.0.0"'):
        return False
    
    print_status("Installing PyQt5...")
    if not run_command(f'"{venv_python}" -m pip install "PyQt5>=5.15.0"'):
        return False
        
    print_status("Installing PyYAML...")
    if not run_command(f'"{venv_python}" -m pip install "PyYAML>=6.0"'):
        return False
        
    print_status("Installing markdown...")
    if not run_command(f'"{venv_python}" -m pip install "markdown>=3.4.0"'):
        return False
    
    print_success("Build dependencies installed")
    return True

def verify_files():
    """Verify required files exist"""
    print_status("Verifying required files...")
    
    required_files = ['menu.py', 'font_manager.py', 'config.yml', 'logo.png', 'smallicon.png']
    missing_files = []
    
    for file_name in required_files:
        if not os.path.exists(file_name):
            missing_files.append(file_name)
    
    if missing_files:
        print_error("Missing required files:")
        for file_name in missing_files:
            print(f"  - {file_name}")
        return False
    
    print_success("All required files found")
    return True

def create_spec_file():
    """Create PyInstaller specification file"""
    print_status("Creating PyInstaller specification...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
        'markdown',
        'markdown.extensions',
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
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
'''
    
    with open('menu.spec', 'w') as f:
        f.write(spec_content)
    
    print_success("PyInstaller specification created")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print_status("Building executable with PyInstaller...")
    
    venv_python = get_venv_python()
    
    if not run_command(f"{venv_python} -m PyInstaller menu.spec --clean --noconfirm"):
        print_error("PyInstaller build failed")
        return False
    
    # Check if executable was created
    exe_name = 'menu.exe' if platform.system() == 'Windows' else 'menu'
    exe_path = os.path.join('dist', exe_name)
    
    if not os.path.exists(exe_path):
        print_error(f"Executable not found: {exe_path}")
        return False
    
    # Make executable on Unix systems
    if platform.system() != 'Windows':
        os.chmod(exe_path, 0o755)
    
    # Get file size
    file_size = os.path.getsize(exe_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print_success(f"Executable created: {exe_path}")
    print_status(f"Executable size: {file_size_mb:.1f} MB")
    
    return True

def create_distribution():
    """Create distribution package"""
    print_status("Creating distribution package...")
    
    # Create package directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"menu_{timestamp}"
    package_dir = Path(package_name)
    
    package_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_name = 'menu.exe' if platform.system() == 'Windows' else 'menu'
    exe_src = Path('dist') / exe_name
    exe_dst = package_dir / exe_name
    
    shutil.copy2(exe_src, exe_dst)
    
    # Copy additional files
    additional_files = ['config.yml', 'logo.png', 'smallicon.png', 'greeting.sh', 'run_linux.sh']
    for file_name in additional_files:
        if os.path.exists(file_name):
            shutil.copy2(file_name, package_dir / file_name)
            # Make shell scripts executable
            if file_name.endswith('.sh'):
                os.chmod(package_dir / file_name, 0o755)
    
    # Copy Docs directory for help system
    docs_src = Path('Docs')
    if docs_src.exists():
        docs_dst = package_dir / 'Docs'
        shutil.copytree(docs_src, docs_dst)
        print_status(f"Copied help documentation: {docs_src} -> {docs_dst}")
    
    # Create sample configuration
    sample_config = '''# Sample configuration for Python GUI Menu
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
'''
    
    with open(package_dir / 'config_sample.yml', 'w') as f:
        f.write(sample_config)
    
    # Create README
    readme_content = f'''Python GUI Menu Application
===========================

This is a self-contained executable of the Python GUI Menu application.
No Python installation or virtual environment is required to run this application.

Files in this package:
- {exe_name}: The main executable
- config.yml: Current configuration file
- config_sample.yml: Sample configuration for reference
- logo.png: Logo image (if present)
- smallicon.png: Window icon (if present)
- greeting.sh: Sample script (if present)
- Docs/: Help documentation and configuration (if present)

To run:
{"./" + exe_name if platform.system() != "Windows" else exe_name}

To use a different configuration file:
{"./" + exe_name if platform.system() != "Windows" else exe_name} my_custom_config.yml

To modify the menu:
1. Edit config.yml (or create a new YAML file)
2. Update the menu_items section with your commands
3. Run the executable

Configuration Format:
The application uses YAML configuration files. See config_sample.yml
for examples of the configuration format.

Built on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Platform: {platform.system()} {platform.release()}

For more information, see: https://github.com/your-repo/Python_GUI_Menu
'''
    
    with open(package_dir / 'README.txt', 'w') as f:
        f.write(readme_content)
    
    # Create platform-specific run scripts
    if platform.system() == 'Windows':
        run_script = f'''@echo off
cd /d "%~dp0"
{exe_name}
pause
'''
        with open(package_dir / 'run.bat', 'w') as f:
            f.write(run_script)
    else:
        # Create cross-platform run script for Unix-like systems
        run_script = f'''#!/bin/bash
# Cross-platform run script for the executable
cd "$(dirname "$0")"

# For the standalone executable, we don't need Qt platform detection
# since PyInstaller bundles everything. Just run it directly.
./{exe_name} "$@"
'''
        run_path = package_dir / 'run.sh'
        with open(run_path, 'w') as f:
            f.write(run_script)
        os.chmod(run_path, 0o755)
    
    print_success(f"Distribution package created: {package_dir}")
    
    # Create compressed archive
    try:
        archive_name = f"{package_name}.zip"
        shutil.make_archive(package_name, 'zip', '.', str(package_dir))
        archive_size = os.path.getsize(archive_name) / (1024 * 1024)
        print_success(f"Archive created: {archive_name} ({archive_size:.1f} MB)")
    except Exception as e:
        print_warning(f"Could not create archive: {e}")
    
    return package_name

def cleanup():
    """Clean up build environment"""
    print_status("Cleaning up build environment...")
    
    dirs_to_clean = ['build_venv', 'build']
    files_to_clean = ['menu.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
    
    print_success("Build environment cleaned")

def main():
    """Main build process"""
    print("=" * 49)
    print("Building Python GUI Menu Application")
    print("=" * 49)
    
    # Disable colors on Windows if needed
    Colors.disable_on_windows()
    
    try:
        # Build process
        if not check_prerequisites():
            return 1
        
        clean_build()
        
        if not create_venv():
            return 1
        
        if not install_dependencies():
            return 1
        
        if not verify_files():
            return 1
        
        if not create_spec_file():
            return 1
        
        if not build_executable():
            return 1
        
        package_name = create_distribution()
        
        cleanup()
        
        # Success summary
        print()
        print("=" * 49)
        print_success("BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 49)
        print()
        print(f"Distribution package: {package_name}")
        if os.path.exists(f"{package_name}.zip"):
            print(f"Compressed archive: {package_name}.zip")
        print()
        print("To test the executable:")
        print(f"  cd {package_name}")
        exe_name = 'menu.exe' if platform.system() == 'Windows' else './menu'
        print(f"  {exe_name}")
        print()
        print("To distribute:")
        print(f"  Share the entire '{package_name}' directory or")
        print(f"  Share the '{package_name}.zip' archive")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print_warning("Build interrupted by user")
        cleanup()
        return 1
    except Exception as e:
        print_error(f"Build failed: {e}")
        cleanup()
        return 1

if __name__ == "__main__":
    sys.exit(main())
