#!/bin/bash
# Run script for Python GUI Menu with font fixes
cd "$(dirname "$0")"
source menu_venv/bin/activate
python menu.py &
exit
