import sys
import os
import yaml
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QLabel, QTextEdit, QFrame, QStackedWidget)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt

class MenuApplication(QMainWindow):
    def __init__(self, config_file):
        super().__init__()
        self.config = self.load_config(config_file)
        self.init_ui()
        
    def load_config(self, config_file):
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set window title
        menu_title = self.config.get('menu_title', 'Menu Application')
        self.setWindowTitle(menu_title)
        
        # Set window icon
        icon_path = self.config.get('icon', '')
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo at the top
        logo_path = self.config.get('logo', '')
        if logo_path and os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(logo_label)
            
            # Add some spacing after logo
            spacer = QWidget()
            spacer.setFixedHeight(20)
            main_layout.addWidget(spacer)
        
        # Title label
        title_label = QLabel(menu_title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create stacked widget for main content and submenus
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create main menu page
        main_menu_widget = QWidget()
        main_menu_layout = QVBoxLayout(main_menu_widget)
        main_menu_layout.setSpacing(10)
        
        # Create the main menu page first
        self.stacked_widget.addWidget(main_menu_widget)
        
        # Add buttons for each separator
        menu_items = self.config.get('menu_items', [])
        
        for i, separator in enumerate(menu_items):
            separator_name = separator.get('name', f'Menu {i+1}')
            separator_button = QPushButton(separator_name)
            separator_button.setMinimumHeight(50)
            
            # Style the button
            separator_button.setStyleSheet("""
                QPushButton {
                    background-color: #4a86e8;
                    color: white;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #3d76d1;
                }
                QPushButton:pressed {
                    background-color: #2c5aa0;
                }
            """)
            
            # Create submenu page for this separator
            submenu_page = self.create_submenu_page(separator)
            page_index = self.stacked_widget.addWidget(submenu_page)
            
            # Connect button to show its submenu
            separator_button.clicked.connect(lambda checked, idx=page_index: 
                                           self.stacked_widget.setCurrentIndex(idx))
            
            main_menu_layout.addWidget(separator_button)
        
        # Add some spacing before exit button
        main_menu_layout.addStretch()
        
        # Add exit button to the main menu
        exit_button = QPushButton("Exit Application")
        exit_button.setMinimumHeight(50)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e06666;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc5050;
            }
            QPushButton:pressed {
                background-color: #b94343;
            }
        """)
        exit_button.clicked.connect(self.close)
        main_menu_layout.addWidget(exit_button)
        
        # Output text area at the bottom
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        self.output_text.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        main_layout.addWidget(QLabel("Command Output:"))
        main_layout.addWidget(self.output_text)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Set window size
        self.resize(500, 700)
        self.setMinimumWidth(400)
        
        # Set initial page
        self.stacked_widget.setCurrentIndex(0)
    
    def create_submenu_page(self, separator):
        """Create a page for the submenu items"""
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        page_layout.setSpacing(10)
        
        # Add title for the submenu
        submenu_title = QLabel(separator.get('name', 'Submenu'))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        submenu_title.setFont(title_font)
        submenu_title.setAlignment(Qt.AlignCenter)
        page_layout.addWidget(submenu_title)
        
        # Add a line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        page_layout.addWidget(line)
        
        # Add buttons for each item in the submenu
        items = separator.get('items', [])
        for item in items:
            item_name = item.get('name', '')
            command = item.get('command', '')
            
            if item_name and command:
                item_button = QPushButton(item_name)
                item_button.setMinimumHeight(40)
                
                # Style the button - using blue style like main menu buttons
                item_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4a86e8;
                        color: white;
                        border-radius: 5px;
                        font-size: 13px;
                        text-align: left;
                        padding-left: 15px;
                    }
                    QPushButton:hover {
                        background-color: #3d76d1;
                    }
                    QPushButton:pressed {
                        background-color: #2c5aa0;
                    }
                """)
                
                # Connect button to execute command
                item_button.clicked.connect(lambda checked, cmd=command: self.execute_command(cmd))
                
                page_layout.addWidget(item_button)
        
        # Add spacing between buttons and back button
        page_layout.addStretch()
        
        # Add back button
        back_button = QPushButton("Back to Main Menu")
        back_button.setMinimumHeight(40)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #6aa84f;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5d9745;
            }
            QPushButton:pressed {
                background-color: #4d7e3a;
            }
        """)
        # Direct connection to go back to main menu
        back_button.clicked.connect(self.go_back_to_main)
        page_layout.addWidget(back_button)
        
        return page_widget
    
    def go_back_to_main(self):
        """Go back to the main menu"""
        self.stacked_widget.setCurrentIndex(0)
    
    def execute_command(self, command):
        """Execute the command and show output in the text area"""
        try:
            output = subprocess.check_output(command, shell=True, universal_newlines=True)
            self.output_text.setHtml(f"<pre style='color: #333333;'>{output}</pre>")
        except subprocess.CalledProcessError as e:
            self.output_text.setHtml(f"<pre style='color: #cc0000;'>Command failed with error code {e.returncode}:\n{e.output}</pre>")


if __name__ == "__main__":
    # Default config file path
    config_file = "config.yml"
    
    # Allow passing config file as argument
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    
    app = QApplication(sys.argv)
    window = MenuApplication(config_file)
    window.show()
    sys.exit(app.exec_())