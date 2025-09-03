Python GUI Menu Application
===========================

This is a self-contained executable of the Python GUI Menu application.
No Python installation or virtual environment is required to run this application.

Files in this package:
- menu: The main executable
- config.yml: Current configuration file
- config_sample.yml: Sample configuration for reference
- logo.png: Logo image (if present)
- smallicon.png: Window icon (if present)
- greeting.sh: Sample script (if present)
- Docs/: Help documentation and configuration (if present)

To run:
./menu

To use a different configuration file:
./menu my_custom_config.yml

To modify the menu:
1. Edit config.yml (or create a new YAML file)
2. Update the menu_items section with your commands
3. Run the executable

Configuration Format:
The application uses YAML configuration files. See config_sample.yml
for examples of the configuration format.

Built on: 2025-09-02 21:40:07
Platform: Linux 6.16.3-200.fc42.x86_64

For more information, see: https://github.com/your-repo/Python_GUI_Menu
