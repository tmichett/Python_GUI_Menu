#!/bin/bash
# Cross-platform run script for the executable
cd "$(dirname "$0")"

# For the standalone executable, we don't need Qt platform detection
# since PyInstaller bundles everything. Just run it directly.
./menu "$@"
