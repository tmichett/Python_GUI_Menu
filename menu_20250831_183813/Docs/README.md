# Python GUI Menu Application - Help Guide

![RHCI Foundation Logo](../logo.png)

## Overview

The Python GUI Menu Application is a PyQt5-based graphical user interface designed to provide an intuitive menu system for executing commands and managing tasks. The application features a customizable, multi-column layout with real-time command execution and output display.

## Features

### Core Functionality
- **Multi-Column Layout**: Organize menu items in multiple columns for better space utilization
- **Real-Time Command Execution**: Execute shell commands with live output streaming
- **Interactive Terminal**: Send input to running processes through built-in terminal interface
- **Detachable Output Window**: Pop out command output to a separate window for better workflow
- **Configurable Interface**: Customize appearance, logos, and layout through YAML configuration
- **Submenu Support**: Organize commands in hierarchical menu structures
- **Responsive Design**: Adaptive layout that scales with content and screen size

### Advanced Features
- **Process Management**: Start, stop, and interact with long-running processes
- **Output Formatting**: Syntax highlighting and proper formatting of terminal output
- **Font Management**: Automatic selection of optimal monospace fonts across platforms
- **Tooltip Support**: Detailed descriptions for menu items and buttons
- **Error Handling**: Comprehensive error reporting and graceful failure recovery

## Getting Started

### Prerequisites

#### System Requirements
- Linux-based operating system (tested on Fedora/RHEL)
- Python 3.6 or higher
- PyQt5 library and dependencies

#### Python Dependencies
```bash
pip install PyQt5 PyYAML
```

### Installation

1. **Clone or Download**: Obtain the application files
2. **Install Dependencies**: Install required Python packages
3. **Configure**: Set up your `config.yml` file
4. **Run**: Execute the application

```bash
# Basic execution
python menu.py

# With custom config file
python menu.py custom_config.yml
```

## Configuration Guide

The application is configured through a YAML file (default: `config.yml`). This file defines the appearance, behavior, and menu structure.

### Basic Configuration

```yaml
# Application appearance
icon: smallicon.png              # Window icon
logo: logo.png                   # Main logo image
logo_size: 320x240              # Logo dimensions (width x height)
menu_title: "Your Application Title"  # Window and main title
menu_help: "python help_system.py"    # Help command to execute

# Layout configuration
num_columns: 2                   # Number of columns in main menu
```

### Menu Structure

The menu system supports hierarchical organization with main menu items and submenus:

```yaml
menu_items:
  - name: "Main Category"        # Display name
    column: 1                    # Column placement (1-based)
    submenu_columns: 2           # Columns in submenu (optional)
    button_info: |               # Tooltip text (optional)
      Detailed description of what this category contains
    items:                       # Submenu items
      - name: "Action Item"      # Submenu item name
        column: 1                # Submenu column (1-based)
        command: "echo 'Hello'"  # Command to execute
        button_info: |           # Item tooltip (optional)
          What this specific action does
```

### Advanced Configuration Options

#### Multi-Column Layouts
- **Main Menu Columns**: Set `num_columns` to organize main categories
- **Submenu Columns**: Use `submenu_columns` for individual submenu layouts
- **Column Assignment**: Use `column` property to specify placement

#### Visual Customization
- **Logo Sizing**: Specify exact dimensions with `logo_size`
- **Window Sizing**: Automatically calculated based on logo and column count
- **Color Schemes**: Built-in styling with hover effects and state changes

## User Interface Guide

### Main Window Layout

#### Top Section
- **Logo Area**: Displays configured logo image
- **Title Bar**: Shows application title with Help button in top-right corner
- **Main Menu**: Grid or list of primary category buttons

#### Middle Section
- **Submenu Area**: Context-sensitive submenu display
- **Navigation**: Back buttons to return to main menu

#### Bottom Section
- **Output Terminal**: Real-time command output display
- **Input Field**: Send input to running processes
- **Control Buttons**: Clear output, detach window controls

### Navigation Flow

1. **Start**: Main menu with category buttons
2. **Select Category**: Click main menu button to enter submenu
3. **Execute Action**: Click submenu item to run command
4. **View Output**: Watch real-time output in terminal area
5. **Interact**: Send input to running processes if needed
6. **Navigate Back**: Use "Back to Main Menu" button

### Output Management

#### Built-in Terminal
- **Real-time Output**: Live streaming of command output
- **Error Highlighting**: Different colors for errors vs. normal output
- **Input Support**: Send text input to running processes
- **Auto-scroll**: Automatically follows output

#### Detachable Window
- **Pop-out**: Click "Detach Output" to open separate window
- **Synchronized**: Both windows show identical output
- **Independent Input**: Send input from either window
- **Window Management**: Close detached window anytime

### Process Management

#### Command Execution
- Commands execute in separate processes
- Output streams in real-time
- Support for interactive programs
- Proper handling of both stdout and stderr

#### Interactive Programs
- **Input Field**: Type commands or responses
- **Send Button**: Submit input to running process
- **Enter Key**: Quick input submission
- **Process State**: Input only available when process is running

## Help System

### Accessing Help
- Click the **Help** button in the top-right corner of the main window
- Help content is defined in `help_config.yml`
- Supports markdown rendering with graphics and links

### Help Configuration

The help system uses `help_config.yml` to define:
- Default help document
- Available help topics
- Graphics and resources

```yaml
help_config: README.md           # Default help document
help_graphic: ../logo.png        # Help system logo
help_topics:                     # Available help topics
  - topic: "Topic Name"          # Display name
    document: "path/to/file.md"  # Markdown file path
```

### Help Features
- **Markdown Rendering**: Full markdown support with formatting
- **Graphics Support**: Display images and graphics
- **Hyperlinks**: Working links to external resources
- **Table of Contents**: Automatic topic index generation
- **Navigation**: Easy browsing between help topics

## Command Execution

### Supported Commands

The application can execute any shell command or script:
- **Shell Commands**: `ls`, `grep`, `find`, etc.
- **Scripts**: Bash, Python, or other executable scripts
- **Programs**: Any command-line application
- **Interactive Tools**: Programs requiring user input

### Command Features

#### Real-time Output
- Live streaming of command output
- Immediate display of results
- Progress indicators for long-running tasks

#### Error Handling
- Clear distinction between normal output and errors
- Exit code reporting
- Process state monitoring

#### Interactive Support
- Send input to running programs
- Support for password prompts
- Menu-driven program navigation

### Best Practices

#### Command Design
```yaml
# Good: Clear, descriptive commands
- name: "Update System Packages"
  command: "sudo dnf update -y"
  
# Good: Script execution
- name: "Run Setup Script"
  command: "./scripts/setup.sh"
  
# Good: Complex operations
- name: "Deploy Application"
  command: "ansible-playbook -i inventory deploy.yml"
```

#### Error Prevention
```yaml
# Include error checking
- name: "Safe File Operation"
  command: "[ -f /path/to/file ] && cp /path/to/file /backup/ || echo 'File not found'"
  
# Use absolute paths
- name: "Run Analysis"
  command: "/home/user/tools/analyze.py --config /etc/analysis.conf"
```

## Troubleshooting

### Common Issues

#### Application Won't Start
**Problem**: Import errors or missing dependencies
```
ImportError: No module named 'PyQt5'
```
**Solution**: Install required packages
```bash
pip install PyQt5 PyYAML
# or
sudo dnf install python3-qt5 python3-pyyaml
```

#### Configuration Errors
**Problem**: YAML syntax errors in config file
```
yaml.scanner.ScannerError: mapping values are not allowed here
```
**Solution**: Validate YAML syntax
```bash
python -c "import yaml; yaml.safe_load(open('config.yml'))"
```

#### Font Issues
**Problem**: Text appears with wrong font or encoding issues
**Solution**: The application automatically selects appropriate fonts, but you can verify font availability:
```bash
fc-list | grep mono  # List available monospace fonts
```

#### Command Execution Issues
**Problem**: Commands fail to execute or show no output
**Solution**: 
- Verify command syntax in terminal first
- Check file permissions for scripts
- Use absolute paths for commands and files
- Add verbose flags to commands for debugging

### Debug Mode

#### Verbose Output
Run with debug information:
```bash
# Enable Qt debug output
export QT_LOGGING_RULES="*=true"
python menu.py
```

#### Configuration Testing
Test configuration without running GUI:
```python
import yaml
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)
    print(yaml.dump(config, indent=2))
```

### Performance Optimization

#### Large Output Handling
For commands with extensive output:
- Terminal has built-in line limits (5000 lines)
- Use output redirection for very large files
- Consider pagination for long results

#### Memory Management
- Detach output window for long-running processes
- Clear output regularly during extended sessions
- Monitor system resources for heavy operations

## Advanced Usage

### Custom Scripts Integration

#### Python Scripts
```yaml
- name: "Run Analysis"
  command: "python3 /path/to/analysis.py --input data.csv --output results.json"
```

#### Ansible Playbooks
```yaml
- name: "Deploy Infrastructure"
  command: "ansible-playbook -i production.ini deploy.yml"
```

#### System Administration
```yaml
- name: "System Health Check"
  command: "systemctl status important-service && df -h && free -m"
```

### Environment Configuration

#### Working Directory
Commands execute from the application's working directory. For scripts in other locations:
```yaml
- name: "Remote Script"
  command: "cd /path/to/scripts && ./script.sh"
```

#### Environment Variables
```yaml
- name: "Environment-aware Command"
  command: "export VAR=value && /path/to/command"
```

### Multi-step Operations

#### Chained Commands
```yaml
- name: "Backup and Update"
  command: "cp config.conf config.conf.bak && wget -O config.conf http://example.com/new-config"
```

#### Conditional Operations
```yaml
- name: "Conditional Deployment"
  command: "[ -f ready.flag ] && deploy.sh || echo 'Not ready for deployment'"
```

## Security Considerations

### Command Safety
- **Input Validation**: Validate all command parameters
- **Path Safety**: Use absolute paths to prevent directory traversal
- **Privilege Management**: Run with minimal required permissions
- **Command Injection**: Avoid dynamic command construction from user input

### File Permissions
```bash
# Secure configuration files
chmod 600 config.yml
chmod 600 help_config.yml

# Executable scripts
chmod 755 scripts/*.sh
```

### Network Operations
For commands that access network resources:
- Use secure protocols (HTTPS, SSH)
- Validate certificates and keys
- Implement timeout mechanisms
- Handle network failures gracefully

## Customization Examples

### Educational Environment
```yaml
menu_title: "Student Lab Environment"
logo_size: 400x200
num_columns: 3

menu_items:
  - name: "Lab Exercises"
    column: 1
    items:
      - name: "Lab 1: Basic Commands"
        command: "./labs/lab1.sh"
      - name: "Lab 2: File Operations"
        command: "./labs/lab2.sh"
        
  - name: "Reference Materials"
    column: 2
    items:
      - name: "Command Reference"
        command: "less /usr/share/doc/commands.txt"
      - name: "Help Documentation"
        command: "man intro"
```

### System Administration
```yaml
menu_title: "System Administration Console"
num_columns: 2

menu_items:
  - name: "System Monitoring"
    column: 1
    submenu_columns: 2
    items:
      - name: "System Status"
        column: 1
        command: "systemctl status"
      - name: "Resource Usage"
        column: 2
        command: "top -n 1"
        
  - name: "Maintenance"
    column: 2
    items:
      - name: "Update System"
        command: "sudo dnf update"
      - name: "Clean Packages"
        command: "sudo dnf autoremove"
```

### Development Environment
```yaml
menu_title: "Development Tools"
num_columns: 1

menu_items:
  - name: "Testing"
    submenu_columns: 3
    items:
      - name: "Unit Tests"
        column: 1
        command: "python -m pytest tests/unit/"
      - name: "Integration Tests"
        column: 2
        command: "python -m pytest tests/integration/"
      - name: "Linting"
        column: 3
        command: "flake8 src/"
```

## Conclusion

The Python GUI Menu Application provides a powerful, flexible interface for command execution and process management. Its configuration-driven approach allows for easy customization while maintaining a consistent, user-friendly experience.

For additional support or to report issues, please refer to the project documentation or contact the development team.

---

*This help system is integrated into the application and accessible through the Help button in the main interface.*
