#!/usr/bin/env python3
"""
Test script to verify build environment and dependencies
This script checks if all required components are available for building
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def test_python():
    """Test Python installation"""
    print("Testing Python installation...")
    try:
        version = sys.version_info
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} found")
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("  ⚠ Warning: Python 3.8+ recommended for PyInstaller")
            return False
        return True
    except Exception as e:
        print(f"  ✗ Python test failed: {e}")
        return False

def test_pip():
    """Test pip installation"""
    print("Testing pip...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"  ✓ {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"  ✗ pip test failed: {e}")
        return False

def test_required_files():
    """Test that required files exist"""
    print("Testing required files...")
    required_files = [
        'menu.py',
        'font_manager.py',
        'config.yml', 
        'logo.png',
        'smallicon.png',
        'requirements_build.txt',
        'build.py',
        'build.sh'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} (missing)")
            missing.append(file)
    
    return len(missing) == 0

def test_build_dependencies():
    """Test if build dependencies can be installed"""
    print("Testing build dependencies installation...")
    
    # Create a temporary virtual environment
    test_venv = "test_venv"
    try:
        print(f"  Creating test virtual environment: {test_venv}")
        subprocess.run([sys.executable, '-m', 'venv', test_venv], 
                      check=True, capture_output=True)
        
        # Get Python path in venv
        if os.name == 'nt':  # Windows
            venv_python = os.path.join(test_venv, 'Scripts', 'python.exe')
        else:
            venv_python = os.path.join(test_venv, 'bin', 'python')
        
        print("  Installing build requirements...")
        subprocess.run([venv_python, '-m', 'pip', 'install', '-r', 'requirements_build.txt'],
                      check=True, capture_output=True)
        
        print("  Testing PyInstaller import...")
        subprocess.run([venv_python, '-c', 'import PyInstaller; print("PyInstaller OK")'],
                      check=True, capture_output=True)
        
        print("  Testing PyQt5 import...")
        subprocess.run([venv_python, '-c', 'import PyQt5.QtWidgets; print("PyQt5 OK")'],
                      check=True, capture_output=True)
        
        print("  Testing PyYAML import...")
        subprocess.run([venv_python, '-c', 'import yaml; print("PyYAML OK")'],
                      check=True, capture_output=True)
        
        print("  ✓ All build dependencies can be installed and imported")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Build dependency test failed: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False
    finally:
        # Clean up test environment
        if os.path.exists(test_venv):
            shutil.rmtree(test_venv)
            print(f"  Cleaned up {test_venv}")

def test_yaml_config():
    """Test that the current config file is valid"""
    print("Testing YAML configuration...")
    try:
        import yaml
        with open('config.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Check basic structure
        required_keys = ['menu_title', 'menu_items']
        for key in required_keys:
            if key not in config:
                print(f"  ⚠ Warning: Missing key '{key}' in config.yml")
            else:
                print(f"  ✓ Found {key}: {config[key] if key == 'menu_title' else f'{len(config[key])} items'}")
        
        print("  ✓ YAML configuration is valid")
        return True
        
    except ImportError:
        print("  ⚠ PyYAML not installed, installing temporarily...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyYAML'], 
                          check=True, capture_output=True)
            return test_yaml_config()  # Retry
        except Exception as e:
            print(f"  ✗ Could not install PyYAML: {e}")
            return False
    except Exception as e:
        print(f"  ✗ YAML test failed: {e}")
        return False

def test_build_scripts():
    """Test that build scripts are executable"""
    print("Testing build scripts...")
    
    scripts = [
        ('build.py', 'Python build script'),
        ('build.sh', 'Shell build script (Unix/Linux/macOS)'),
        ('build.bat', 'Batch build script (Windows)')
    ]
    
    all_good = True
    for script, description in scripts:
        if os.path.exists(script):
            if script.endswith('.sh'):
                if os.access(script, os.X_OK):
                    print(f"  ✓ {script} - {description} (executable)")
                else:
                    print(f"  ⚠ {script} - {description} (not executable)")
                    print(f"    Run: chmod +x {script}")
            else:
                print(f"  ✓ {script} - {description}")
        else:
            print(f"  ✗ {script} - {description} (missing)")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("=" * 50)
    print("Python GUI Menu - Build Environment Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Python Installation", test_python),
        ("Pip Package Manager", test_pip),
        ("Required Files", test_required_files),
        ("YAML Configuration", test_yaml_config),
        ("Build Scripts", test_build_scripts),
        ("Build Dependencies", test_build_dependencies),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"{symbol} {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your build environment is ready.")
        print("   Run 'python build.py' to create a standalone executable.")
    else:
        print(f"\n⚠ {len(results) - passed} test(s) failed. Check the errors above.")
        print("   Fix the issues before building.")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
