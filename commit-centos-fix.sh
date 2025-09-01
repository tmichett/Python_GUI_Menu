#!/bin/bash
# Script to commit the CentOS Stream 9 compatibility fixes

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

print_status "Committing CentOS Stream 9 compatibility fixes..."

# Check if we have uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    print_status "Found uncommitted changes, proceeding with commit..."
    
    # Add all the modified files
    git add .github/workflows/build-rpm.yml
    git add RPM_PACKAGING.md  
    git add build-rpm.sh
    git add CENTOS_STREAM9_FIX.md
    git add commit-centos-fix.sh
    
    # Show what's being committed
    print_status "Files being committed:"
    git diff --cached --name-only
    
    # Commit with descriptive message
    git commit -m "Fix CentOS Stream 9 build compatibility

- Replace python3-venv with python3-devel in dependencies
- Fix changelog date generation in RPM spec file  
- Update documentation with CentOS Stream 9 specifics
- Add troubleshooting guide for common build issues

Fixes GitHub Action build failure:
- No match for argument: python3-venv
- bad date in %changelog error

The venv module is built into python3 package in CentOS Stream 9,
and python3-devel provides the development headers needed for
PyInstaller and PyQt5 native extensions."
    
    print_success "Changes committed successfully!"
    
    # Ask about pushing
    echo ""
    echo "Next steps:"
    echo "1. Push to GitHub:"
    echo "   git push"
    echo ""
    echo "2. Create and push a test tag:"
    echo "   git tag v1.0.2"
    echo "   git push origin v1.0.2"
    echo ""
    echo "3. Or manually trigger GitHub Action workflow"
    
else
    print_warning "No uncommitted changes found. All files are already committed."
    
    # Show current status
    print_status "Current git status:"
    git status --porcelain
fi

print_status "Summary of fixes applied:"
echo "✅ Removed python3-venv dependency (not available in CentOS Stream 9)"
echo "✅ Added python3-devel dependency (provides development headers)"  
echo "✅ Fixed changelog date generation in GitHub Action"
echo "✅ Updated documentation and troubleshooting guide"
echo ""
print_success "Ready to test the build process!"
