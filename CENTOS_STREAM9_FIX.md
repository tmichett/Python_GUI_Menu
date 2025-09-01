# CentOS Stream 9 Build Fix

## Issue Description

The GitHub Action was failing during the dependency installation step with the error:

```
No match for argument: python3-venv
Error: Unable to find a match: python3-venv
Error: Process completed with exit code 1.
```

## Root Cause

In CentOS Stream 9, the `python3-venv` package doesn't exist as a separate package. The `venv` module is included directly in the base `python3` package, unlike some other distributions where it's packaged separately.

## Fix Applied

### 1. Updated GitHub Action Workflow

**File**: `.github/workflows/build-rpm.yml`

**Changed**:
```yaml
# OLD - BROKEN
python3-venv \

# NEW - WORKING  
python3-devel \
```

### 2. Updated Documentation

**File**: `RPM_PACKAGING.md`

- Updated prerequisite package lists
- Added specific troubleshooting section for this error
- Corrected build dependency documentation

## Why This Fix Works

1. **`python3-devel`**: Provides Python development headers needed for compiling native extensions (required by PyInstaller and some PyQt5 components)

2. **Built-in venv**: The `venv` module is available directly via `python3 -m venv` without needing additional packages

3. **CentOS Stream 9 compatibility**: Uses packages that actually exist in the CentOS Stream 9 repositories

## Package Differences by Distribution

| Distribution | Virtual Environment Package | Development Headers |
|-------------|----------------------------|-------------------|
| CentOS Stream 9 | Built into `python3` | `python3-devel` |
| CentOS/RHEL 8 | Built into `python3` | `python3-devel` |
| Ubuntu/Debian | `python3-venv` | `python3-dev` |
| Fedora | Built into `python3` | `python3-devel` |

## Additional Issue: Debug Package Generation

### Problem
```
error: Empty %files file /github/home/rpmbuild/BUILD/python-gui-menu-1.0.2/debugsourcefiles.list
```

### Root Cause
RPM was trying to create debug packages for debugging information, but since we're packaging a pre-built PyInstaller executable (not compiling from source), there are no debug source files to include.

### Fix Applied
Added debug package disabling directives to the RPM spec file:
```rpm
%global _enable_debug_package 0
%global debug_package %{nil}
```

## Verification

After applying this fix, the GitHub Action should:

1. ✅ Successfully install all system dependencies
2. ✅ Create virtual environment using `python3 -m venv`
3. ✅ Build the application using PyInstaller
4. ✅ Create RPM package successfully (no debug package errors)
5. ✅ Pass installation tests

## Testing the Fix

To test locally on CentOS Stream 9:

```bash
# Verify the correct packages are available
dnf search python3-devel
dnf info python3

# Test venv creation
python3 -m venv test_env
source test_env/bin/activate
pip install --upgrade pip
deactivate
rm -rf test_env
```

This fix ensures compatibility with CentOS Stream 9's package structure while maintaining the cross-platform enhanced build functionality.
