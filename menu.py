import sys
import os
import yaml
import subprocess
import markdown
import re
import unicodedata
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QLabel, QTextEdit, QFrame, QStackedWidget,
                            QHBoxLayout, QGridLayout, QDialog, QSplitter, QLineEdit,
                            QTextBrowser, QListWidget, QListWidgetItem, QScrollArea)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QDesktopServices
from PyQt5.QtCore import Qt, QProcess, pyqtSignal, QObject, QUrl
from font_manager import get_font_manager

class OutputTerminal(QTextEdit):
    """Custom QTextEdit that formats and displays terminal output"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        
        # Get the best monospace font for this system
        font_manager = get_font_manager()
        monospace_css = font_manager.get_monospace_font_css()
        
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: #f0f0f0;
                border-radius: 5px;
                padding: 10px;
                {monospace_css}
                font-size: 12px;
            }}
        """)
        self.document().setMaximumBlockCount(5000)  # Limit to prevent memory issues
    
    def append_output(self, text, error=False):
        """Append text to the terminal with appropriate formatting"""
        
        # Clean and format the text first (this includes ANSI-to-HTML conversion)
        text = self.clean_and_format_text(text)
        
        # Process text to handle newlines properly
        default_color = "#cc0000" if error else "#333333"
        
        # Check if text already contains HTML spans (from ANSI conversion)
        has_html_formatting = '<span' in text
        
        if not has_html_formatting:
            # HTML escape only if no HTML formatting is present
            text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Replace newlines with HTML line breaks
        text = text.replace("\n", "<br>")
        
        # Ensure carriage returns are handled correctly (terminal-like behavior)
        if "\r" in text and not text.endswith("\r"):
            lines = text.split("\r")
            # Replace the last line in the document
            cursor = self.textCursor()
            cursor.movePosition(cursor.End)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
            if has_html_formatting:
                cursor.insertHtml(lines[-1])
            else:
                cursor.insertHtml(f"<span style='color: {default_color};'>{lines[-1]}</span>")
        else:
            # Normal append for text without carriage returns
            if has_html_formatting:
                # Text already has HTML formatting from ANSI conversion
                self.insertHtml(text)
            else:
                # Apply default color
                self.append(f"<span style='color: {default_color};'>{text}</span>")
        
        # Scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clean_and_format_text(self, text):
        """Convert ANSI escape sequences to HTML formatting and clean non-printable characters"""
        if not text:
            return text
        
        # Convert ANSI escape sequences to HTML
        text = self.ansi_to_html(text)
        
        # Remove other common escape sequences
        # Bell character (ASCII 7)
        text = text.replace('\x07', '')
        
        # Backspace (ASCII 8) - remove it and the previous character
        while '\x08' in text:
            pos = text.find('\x08')
            if pos > 0:
                text = text[:pos-1] + text[pos+1:]
            else:
                text = text[pos+1:]
        
        # Form feed (ASCII 12)
        text = text.replace('\x0c', '\n')
        
        # Vertical tab (ASCII 11)
        text = text.replace('\x0b', '\n')
        
        # Handle other control characters (0-31 except tab, newline, carriage return)
        cleaned_chars = []
        for char in text:
            code = ord(char)
            if code < 32:  # Control characters
                if char in ['\t', '\n', '\r']:
                    # Keep these useful control characters
                    cleaned_chars.append(char)
                else:
                    # Replace other control characters with placeholder or remove
                    continue
            elif code == 127:  # DEL character
                continue
            elif unicodedata.category(char).startswith('C') and char not in ['\t', '\n', '\r']:
                # Other Unicode control characters (except tab, newline, carriage return)
                continue
            else:
                cleaned_chars.append(char)
        
        return ''.join(cleaned_chars)
    
    def ansi_to_html(self, text):
        """Convert ANSI escape sequences to HTML formatting"""
        if not text:
            return text
        
        # ANSI color mapping to HTML colors
        ansi_colors = {
            '30': '#000000',  # Black
            '31': '#cd0000',  # Red
            '32': '#00cd00',  # Green
            '33': '#cdcd00',  # Yellow
            '34': '#0000ee',  # Blue
            '35': '#cd00cd',  # Magenta
            '36': '#00cdcd',  # Cyan
            '37': '#e5e5e5',  # White
            '90': '#7f7f7f',  # Bright Black (Gray)
            '91': '#ff0000',  # Bright Red
            '92': '#00ff00',  # Bright Green
            '93': '#ffff00',  # Bright Yellow
            '94': '#5c5cff',  # Bright Blue
            '95': '#ff00ff',  # Bright Magenta
            '96': '#00ffff',  # Bright Cyan
            '97': '#ffffff',  # Bright White
        }
        
        ansi_bg_colors = {
            '40': '#000000',  # Black background
            '41': '#cd0000',  # Red background
            '42': '#00cd00',  # Green background
            '43': '#cdcd00',  # Yellow background
            '44': '#0000ee',  # Blue background
            '45': '#cd00cd',  # Magenta background
            '46': '#00cdcd',  # Cyan background
            '47': '#e5e5e5',  # White background
            '100': '#7f7f7f', # Bright Black background
            '101': '#ff0000', # Bright Red background
            '102': '#00ff00', # Bright Green background
            '103': '#ffff00', # Bright Yellow background
            '104': '#5c5cff', # Bright Blue background
            '105': '#ff00ff', # Bright Magenta background
            '106': '#00ffff', # Bright Cyan background
            '107': '#ffffff', # Bright White background
        }
        
        # Current formatting state
        current_style = {
            'color': None,
            'bg_color': None,
            'bold': False,
            'italic': False,
            'underline': False
        }
        
        result = []
        i = 0
        
        while i < len(text):
            # Look for ANSI escape sequence
            if text[i:i+2] == '\x1b[':
                # Find the end of the escape sequence
                j = i + 2
                while j < len(text) and text[j] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz':
                    j += 1
                
                if j < len(text):
                    # Extract the command
                    command = text[i+2:j]
                    end_char = text[j]
                    
                    if end_char == 'm':  # Color/formatting command
                        # Parse the parameters
                        params = command.split(';') if command else ['0']
                        
                        for param in params:
                            param = param.strip()
                            if not param:
                                param = '0'
                                
                            if param == '0':  # Reset
                                current_style = {
                                    'color': None,
                                    'bg_color': None,
                                    'bold': False,
                                    'italic': False,
                                    'underline': False
                                }
                            elif param == '1':  # Bold
                                current_style['bold'] = True
                            elif param == '3':  # Italic
                                current_style['italic'] = True
                            elif param == '4':  # Underline
                                current_style['underline'] = True
                            elif param == '22':  # Normal intensity (not bold)
                                current_style['bold'] = False
                            elif param == '23':  # Not italic
                                current_style['italic'] = False
                            elif param == '24':  # Not underlined
                                current_style['underline'] = False
                            elif param in ansi_colors:  # Foreground color
                                current_style['color'] = ansi_colors[param]
                            elif param in ansi_bg_colors:  # Background color
                                current_style['bg_color'] = ansi_bg_colors[param]
                            elif param == '39':  # Default foreground
                                current_style['color'] = None
                            elif param == '49':  # Default background
                                current_style['bg_color'] = None
                        
                        # Close any open span
                        if result and result[-1] != '</span>':
                            result.append('</span>')
                        
                        # Open new span with current style
                        style_parts = []
                        if current_style['color']:
                            style_parts.append(f"color: {current_style['color']}")
                        if current_style['bg_color']:
                            style_parts.append(f"background-color: {current_style['bg_color']}")
                        if current_style['bold']:
                            style_parts.append("font-weight: bold")
                        if current_style['italic']:
                            style_parts.append("font-style: italic")
                        if current_style['underline']:
                            style_parts.append("text-decoration: underline")
                        
                        if style_parts:
                            style_str = '; '.join(style_parts)
                            result.append(f'<span style="{style_str}">')
                        else:
                            result.append('<span>')
                    
                    i = j + 1
                else:
                    # Malformed escape sequence, just add the character
                    result.append(text[i])
                    i += 1
            else:
                result.append(text[i])
                i += 1
        
        # Close any remaining open span
        text_result = ''.join(result)
        if '<span' in text_result and not text_result.endswith('</span>'):
            text_result += '</span>'
        
        return text_result

class ProcessManager(QObject):
    """Manages command execution and emits output signals"""
    output_received = pyqtSignal(str, bool)  # text, is_error
    process_finished = pyqtSignal(int, QProcess.ExitStatus)  # exit code, exit status
    process_started = pyqtSignal()  # Signal when process starts
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.started.connect(self.process_started)
    
    def execute_command(self, command):
        """Execute a shell command"""
        if self.process.state() == QProcess.Running:
            self.process.kill()
            self.process.waitForFinished()
        
        # Use bash for better terminal compatibility
        self.process.start('bash', ['-c', command])
    
    def handle_stdout(self):
        """Handle standard output data"""
        raw_data = self.process.readAllStandardOutput().data()
        data = self.decode_output(raw_data)
        if data:
            self.output_received.emit(data, False)
    
    def handle_stderr(self):
        """Handle standard error data"""
        raw_data = self.process.readAllStandardError().data()
        data = self.decode_output(raw_data)
        if data:
            self.output_received.emit(data, True)
    
    def decode_output(self, raw_data):
        """Decode raw output data with proper error handling"""
        try:
            # Try UTF-8 first
            return raw_data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Try Latin-1 as fallback (can decode any byte sequence)
                decoded = raw_data.decode('latin-1')
                # Add a note about encoding issues if there are suspicious characters
                if any(ord(c) > 127 for c in decoded):
                    return f"[Encoding issue detected - displaying as Latin-1]\n{decoded}"
                return decoded
            except UnicodeDecodeError:
                # Last resort: replace problematic characters
                return raw_data.decode('utf-8', errors='replace')
    
    def send_input(self, text):
        """Send input to the running process"""
        if self.process.state() == QProcess.Running:
            # Add newline if not present
            if not text.endswith('\n'):
                text += '\n'
            self.process.write(text.encode('utf-8'))
            return True
        return False
    
    def is_running(self):
        """Check if process is running"""
        return self.process.state() == QProcess.Running

class OutputWindow(QDialog):
    """Detachable window for command output"""
    input_sent = pyqtSignal(str)  # Signal when user sends input
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Command Output")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Output terminal
        self.output_terminal = OutputTerminal()
        layout.addWidget(self.output_terminal)
        
        # Add input field
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)
        
        input_label = QLabel("Input:")
        input_label.setFixedWidth(50)
        input_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
                padding: 5px;
            }
        """)
        input_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        
        # Get monospace font for input field
        font_manager = get_font_manager()
        monospace_css = font_manager.get_monospace_font_css()
        
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                color: #333333;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                {monospace_css}
                font-size: 12px;
            }}
            QLineEdit:disabled {{
                background-color: #f0f0f0;
                color: #666666;
            }}
        """)
        self.input_field.returnPressed.connect(self.send_input)
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_input)
        self.send_button.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # Create buttons for the dialog
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear Output")
        self.clear_button.clicked.connect(self.output_terminal.clear)
        button_layout.addWidget(self.clear_button)
        
        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.hide)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def send_input(self):
        """Send input from the input field"""
        text = self.input_field.text()
        if text:
            self.input_sent.emit(text)
            # Display the input in the terminal (user feedback)
            self.output_terminal.append_output(f"> {text}\n", False)
            self.input_field.clear()
    
    def set_input_enabled(self, enabled):
        """Enable or disable the input controls"""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)

class HelpWindow(QDialog):
    """Help window with markdown rendering and navigation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.help_config = {}
        self.current_document = None
        self.help_base_path = ""
        self.init_ui()
        self.load_help_config()
    
    def init_ui(self):
        """Initialize the help window UI"""
        self.setWindowTitle("Application Help")
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        
        # Left panel for table of contents
        toc_frame = QFrame()
        toc_frame.setFrameShape(QFrame.StyledPanel)
        toc_frame.setMaximumWidth(250)
        toc_frame.setMinimumWidth(200)
        toc_layout = QVBoxLayout(toc_frame)
        
        # Table of contents title
        toc_title = QLabel("Help Topics")
        toc_title.setFont(QFont("", 12, QFont.Bold))
        toc_title.setAlignment(Qt.AlignCenter)
        toc_layout.addWidget(toc_title)
        
        # Table of contents list
        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self.on_topic_selected)
        toc_layout.addWidget(self.toc_list)
        
        main_layout.addWidget(toc_frame)
        
        # Right panel for content
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_layout = QVBoxLayout(content_frame)
        
        # Content browser
        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.anchorClicked.connect(self.handle_link_clicked)
        
        # Set up content browser styling
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        content_layout.addWidget(self.content_browser)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        content_layout.addWidget(close_button)
        
        main_layout.addWidget(content_frame)
        
        # Set layout proportions
        main_layout.setStretch(0, 0)  # TOC panel - fixed width
        main_layout.setStretch(1, 1)  # Content panel - expandable
    
    def load_help_config(self):
        """Load help configuration from help_config.yml"""
        help_config_path = os.path.join("Docs", "help_config.yml")
        self.help_base_path = os.path.dirname(help_config_path)
        
        try:
            with open(help_config_path, 'r') as file:
                self.help_config = yaml.safe_load(file) or {}
            self.populate_toc()
            self.load_default_help()
        except Exception as e:
            error_msg = f"<h2>Help System Error</h2><p>Could not load help configuration: {e}</p>"
            error_msg += f"<p>Looking for: <code>{help_config_path}</code></p>"
            self.content_browser.setHtml(error_msg)
    
    def populate_toc(self):
        """Populate the table of contents from help_config"""
        self.toc_list.clear()
        
        # Add main help document
        default_doc = self.help_config.get('help_config', 'README.md')
        main_item = QListWidgetItem("📖 Application Guide")
        main_item.setData(Qt.UserRole, default_doc)
        self.toc_list.addItem(main_item)
        
        # Add help topics
        help_topics = self.help_config.get('help_topics', [])
        for topic in help_topics:
            topic_name = topic.get('topic', 'Unknown Topic')
            document = topic.get('document', '')
            if document:
                item = QListWidgetItem(f"📄 {topic_name}")
                item.setData(Qt.UserRole, document)
                self.toc_list.addItem(item)
    
    def load_default_help(self):
        """Load the default help document"""
        default_doc = self.help_config.get('help_config', 'README.md')
        self.load_document(default_doc)
        
        # Select the first item in the TOC
        if self.toc_list.count() > 0:
            self.toc_list.setCurrentRow(0)
    
    def on_topic_selected(self, item):
        """Handle topic selection from table of contents"""
        document_path = item.data(Qt.UserRole)
        if document_path:
            self.load_document(document_path)
    
    def load_document(self, document_path):
        """Load and render a markdown document"""
        try:
            # Handle relative paths - if the path already starts with Docs/, don't add it again
            if not os.path.isabs(document_path):
                if document_path.startswith("Docs/"):
                    full_path = document_path
                else:
                    full_path = os.path.join("Docs", document_path)
            else:
                full_path = document_path
            
            if not os.path.exists(full_path):
                error_msg = f"<h2>Document Not Found</h2><p>Could not find document: <code>{full_path}</code></p>"
                self.content_browser.setHtml(error_msg)
                return
            
            with open(full_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
            
            # Convert markdown to HTML
            html_content = self.markdown_to_html(markdown_content, os.path.dirname(full_path))
            
            # Set the HTML content
            self.content_browser.setHtml(html_content)
            self.current_document = full_path
            
        except Exception as e:
            error_msg = f"<h2>Error Loading Document</h2><p>Failed to load {document_path}: {e}</p>"
            self.content_browser.setHtml(error_msg)
    
    def markdown_to_html(self, markdown_content, base_path):
        """Convert markdown to HTML with image and link processing"""
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        
        # Convert to HTML
        html_content = md.convert(markdown_content)
        
        # Process images to use absolute paths
        html_content = self.process_images(html_content, base_path)
        
        # Add CSS styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: none;
                    margin: 0;
                    padding: 20px;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 24px;
                    margin-bottom: 16px;
                }}
                h1 {{
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }}
                h2 {{
                    border-bottom: 1px solid #eee;
                    padding-bottom: 8px;
                }}
                code {{
                    background-color: #f8f9fa;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 16px;
                    overflow-x: auto;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                blockquote {{
                    border-left: 4px solid #dfe2e5;
                    padding: 0 16px;
                    color: #6a737d;
                    margin: 16px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 16px 0;
                }}
                th, td {{
                    border: 1px solid #dfe2e5;
                    padding: 8px 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 16px auto;
                    border-radius: 6px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                ul, ol {{
                    margin: 16px 0;
                    padding-left: 32px;
                }}
                li {{
                    margin: 4px 0;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        return styled_html
    
    def process_images(self, html_content, base_path):
        """Process image tags to use absolute file paths"""
        def replace_src(match):
            src = match.group(1)
            # If it's already an absolute path or URL, leave it
            if os.path.isabs(src) or src.startswith(('http://', 'https://', 'file://')):
                return match.group(0)
            
            # Convert relative path to absolute file URL
            if src.startswith('../'):
                # Handle paths like ../logo.png
                abs_path = os.path.abspath(os.path.join(base_path, src))
            else:
                abs_path = os.path.abspath(os.path.join(base_path, src))
            
            if os.path.exists(abs_path):
                file_url = f"file://{abs_path}"
                return f'<img src="{file_url}"' + match.group(0)[match.group(0).find(' '):]
            else:
                # If file doesn't exist, keep original path but add a note
                return f'<img src="{src}" alt="[Image not found: {src}]"' + match.group(0)[match.group(0).find(' '):]
        
        # Replace img src attributes
        img_pattern = r'<img src="([^"]*)"'
        html_content = re.sub(img_pattern, replace_src, html_content)
        
        return html_content
    
    def handle_link_clicked(self, url):
        """Handle clicking on links in the help content"""
        url_string = url.toString()
        
        # Handle file links (other help documents)
        if url_string.startswith('file://') and url_string.endswith('.md'):
            # Extract the file path and load it as a help document
            file_path = url_string.replace('file://', '')
            if os.path.exists(file_path):
                self.load_document(file_path)
            return
        
        # Handle external links
        if url_string.startswith(('http://', 'https://')):
            QDesktopServices.openUrl(url)
            return
        
        # Handle relative links within the same document
        if url_string.startswith('#'):
            # Let the browser handle internal anchors
            return

class MenuApplication(QMainWindow):
    def __init__(self, config_file):
        super().__init__()
        self.config = self.load_config(config_file)
        self.init_ui()
        
        # Create process manager for command execution
        self.process_manager = ProcessManager()
        self.process_manager.output_received.connect(self.update_output)
        self.process_manager.process_finished.connect(self.on_process_finished)
        self.process_manager.process_started.connect(self.on_process_started)
        
        # Create detachable output window
        self.output_window = OutputWindow(self)
        self.output_window.input_sent.connect(self.send_process_input)
        
        # Create help window
        self.help_window = HelpWindow(self)
        
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
        
        # Default window width
        window_width = 500
        
        # Logo at the top
        logo_path = self.config.get('logo', '')
        if logo_path and os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            
            # Check if logo_size is specified in the config
            logo_size = self.config.get('logo_size', '300x100')
            try:
                width, height = map(int, logo_size.split('x'))
                # Update window width to be at least 100px wider than logo
                window_width = max(window_width, width + 100)
            except (ValueError, AttributeError):
                # Default to 300x100 if parsing fails
                width, height = 300, 100
                window_width = max(window_width, width + 100)
                
            logo_label.setPixmap(pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
        
        # Add help button in top right corner
        help_button = QPushButton("Help")
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #5bc0de;
                color: white;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #46b8da;
            }
        """)
        help_button.setFixedWidth(80)
        help_button.setFixedHeight(30)
        
        # Connect help button to help window
        help_button.clicked.connect(self.show_help)
        
        # Create a horizontal layout for the title and help button
        title_layout = QHBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(help_button)
        main_layout.addLayout(title_layout)
        
        # Create stacked widget for main content and submenus
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Create main menu page with multi-column support
        main_menu_widget = QWidget()
        
        # Get number of columns from config (default to 1)
        num_columns = self.config.get('num_columns', 1)
        
        # Create layout based on number of columns
        if num_columns > 1:
            main_menu_layout = QGridLayout(main_menu_widget)
            main_menu_layout.setSpacing(10)
        else:
            main_menu_layout = QVBoxLayout(main_menu_widget)
            main_menu_layout.setSpacing(10)
        
        # Create the main menu page first
        self.stacked_widget.addWidget(main_menu_widget)
        
        # Add buttons for each separator
        menu_items = self.config.get('menu_items', [])
        
        # Track items in each column
        column_items = {i+1: 0 for i in range(num_columns)}
        
        for i, separator in enumerate(menu_items):
            separator_name = separator.get('name', f'Menu {i+1}')
            separator_button = QPushButton(separator_name)
            separator_button.setMinimumHeight(50)
            
            # Add tooltip if button_info is provided
            button_info = separator.get('button_info', '')
            if button_info:
                separator_button.setToolTip(button_info.strip())  # Strip whitespace
                separator_button.setToolTipDuration(5000)  # Show for 5 seconds
            
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
            
            # Get column for this menu item (default to 1)
            column = separator.get('column', 1)
            
            # Ensure column is valid
            if column < 1 or column > num_columns:
                column = 1
                
            # Add button to the appropriate column
            if num_columns > 1:
                row = column_items[column]
                main_menu_layout.addWidget(separator_button, row, column-1)
                column_items[column] += 1
            else:
                main_menu_layout.addWidget(separator_button)
        
        # Add exit button at the bottom, spanning all columns if using grid layout
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
        
        if num_columns > 1:
            # Add some empty space
            for col in range(num_columns):
                main_menu_layout.setColumnStretch(col, 1)
                
            # Add spacer rows
            max_rows = max(column_items.values()) if column_items else 0
            spacer_row = QWidget()
            main_menu_layout.addWidget(spacer_row, max_rows, 0, 1, num_columns)
            main_menu_layout.setRowStretch(max_rows, 1)
            
            # Add exit button spanning all columns
            main_menu_layout.addWidget(exit_button, max_rows + 1, 0, 1, num_columns)
        else:
            main_menu_layout.addStretch()
            main_menu_layout.addWidget(exit_button)
        
        # Create bottom frame for output area with title and controls
        output_frame = QFrame()
        output_frame.setFrameShape(QFrame.StyledPanel)
        output_frame.setStyleSheet("background-color: #f8f8f8; border-radius: 5px;")
        output_layout = QVBoxLayout(output_frame)
        
        # Output header with title and detach button
        output_header = QWidget()
        header_layout = QHBoxLayout(output_header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        output_title = QLabel("Command Output:")
        output_title.setFont(QFont("", 10, QFont.Bold))
        header_layout.addWidget(output_title)
        
        header_layout.addStretch()
        
        # Add detach button
        detach_button = QPushButton("Detach Output")
        detach_button.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        detach_button.clicked.connect(self.detach_output_window)
        header_layout.addWidget(detach_button)
        
        # Add clear button
        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 3px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        clear_button.clicked.connect(self.clear_output)
        header_layout.addWidget(clear_button)
        
        output_layout.addWidget(output_header)
        
        # Output text area
        self.output_text = OutputTerminal()
        output_layout.addWidget(self.output_text)
        
        # Add input field to main window
        input_layout = QHBoxLayout()
        
        input_label = QLabel("Input:")
        input_label.setFixedWidth(50)
        input_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font-weight: bold;
                padding: 5px;
            }
        """)
        input_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        
        # Get monospace font for input field
        font_manager = get_font_manager()
        monospace_css = font_manager.get_monospace_font_css()
        
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: white;
                color: #333333;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                {monospace_css}
                font-size: 12px;
            }}
            QLineEdit:disabled {{
                background-color: #f0f0f0;
                color: #666666;
            }}
        """)
        self.input_field.returnPressed.connect(self.send_input)
        self.input_field.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.input_field)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_input)
        self.send_button.setEnabled(False)  # Initially disabled
        input_layout.addWidget(self.send_button)
        
        output_layout.addLayout(input_layout)
        
        main_layout.addWidget(output_frame)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Set window size based on logo width plus 100px margin
        # If we have multiple columns, increase the width further
        if num_columns > 1:
            window_width = max(window_width, 250 * num_columns + 100)
            
        self.resize(window_width, 900)
        self.setMinimumWidth(window_width)
        
        # Set initial page
        self.stacked_widget.setCurrentIndex(0)
    
    def create_submenu_page(self, separator):
        """Create a page for the submenu items with column support"""
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        page_layout.setSpacing(10)
        
        # Add title for the submenu with MUCH LARGER and BOLDER font
        submenu_title = QLabel(separator.get('name', 'Submenu'))
        title_font = QFont()
        title_font.setPointSize(24)  # Much larger font size
        title_font.setBold(True)
        title_font.setWeight(99)  # Maximum boldness (normal is 50, bold is 75)
        submenu_title.setFont(title_font)
        submenu_title.setAlignment(Qt.AlignCenter)
        
        # No color styling, just bold and large
        page_layout.addWidget(submenu_title)
        
        # Add some spacing after title
        spacer_after_title = QWidget()
        spacer_after_title.setFixedHeight(15)
        page_layout.addWidget(spacer_after_title)
        
        # Add a simple line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        page_layout.addWidget(line)
        
        # Create widget for submenu buttons
        submenu_buttons_widget = QWidget()
        
        # Get number of columns for this submenu (default to 1)
        submenu_columns = separator.get('submenu_columns', 1)
        
        # Create layout based on number of columns
        if submenu_columns > 1:
            submenu_buttons_layout = QGridLayout(submenu_buttons_widget)
            submenu_buttons_layout.setSpacing(10)
        else:
            submenu_buttons_layout = QVBoxLayout(submenu_buttons_widget)
            submenu_buttons_layout.setSpacing(10)
        
        # Track items in each column
        column_items = {i+1: 0 for i in range(submenu_columns)}
        
        # Add buttons for each item in the submenu
        items = separator.get('items', [])
        for item in items:
            item_name = item.get('name', '')
            command = item.get('command', '')
            
            if item_name and command:
                item_button = QPushButton(item_name)
                item_button.setMinimumHeight(40)
                
                # Add tooltip if button_info is provided
                button_info = item.get('button_info', '')
                if button_info:
                    item_button.setToolTip(button_info.strip())  # Strip whitespace
                    item_button.setToolTipDuration(5000)  # Show for 5 seconds
                
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
                
                # Get column for this item (default to 1)
                column = item.get('column', 1)
                
                # Ensure column is valid
                if column < 1 or column > submenu_columns:
                    column = 1
                
                # Add button to the appropriate column
                if submenu_columns > 1:
                    row = column_items[column]
                    submenu_buttons_layout.addWidget(item_button, row, column-1)
                    column_items[column] += 1
                else:
                    submenu_buttons_layout.addWidget(item_button)
        
        # Add column stretching if using grid layout
        if submenu_columns > 1:
            for col in range(submenu_columns):
                submenu_buttons_layout.setColumnStretch(col, 1)
        else:
            submenu_buttons_layout.addStretch()
            
        # Add the submenu buttons widget to the page layout
        page_layout.addWidget(submenu_buttons_widget)
        
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
        """Execute the command and show output in real-time"""
        # Clear output areas
        self.output_text.clear()
        self.output_window.output_terminal.clear()
        
        # Display command that is being executed
        cmd_display = f"Executing: {command}\n{'-' * 50}\n"
        self.output_text.append_output(cmd_display)
        self.output_window.output_terminal.append_output(cmd_display)
        
        # Execute the command
        self.process_manager.execute_command(command)
    
    def update_output(self, text, is_error):
        """Update both output terminals with new text"""
        self.output_text.append_output(text, is_error)
        self.output_window.output_terminal.append_output(text, is_error)
    
    def on_process_started(self):
        """Enable input fields when process starts"""
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.output_window.set_input_enabled(True)
    
    def on_process_finished(self, exit_code, exit_status):
        """Handle process completion"""
        status_text = f"\n{'-' * 50}\nCommand finished with exit code: {exit_code}\n"
        if exit_code != 0:
            self.update_output(status_text, True)  # Show in red for non-zero exit
        else:
            self.update_output(status_text, False)
        
        # Disable input fields when process finishes
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.output_window.set_input_enabled(False)
    
    def send_input(self):
        """Send input from the main window's input field"""
        text = self.input_field.text()
        if text and self.process_manager.is_running():
            # Display the input in both terminals (user feedback)
            self.output_text.append_output(f"> {text}\n", False)
            self.output_window.output_terminal.append_output(f"> {text}\n", False)
            
            # Send to process
            self.process_manager.send_input(text)
            self.input_field.clear()
    
    def send_process_input(self, text):
        """Send input from the detached output window"""
        if self.process_manager.is_running():
            # Send to process (the output window already shows the input)
            self.output_text.append_output(f"> {text}\n", False)  # Show in main window too
            self.process_manager.send_input(text)
    
    def detach_output_window(self):
        """Show the detached output window"""
        self.output_window.show()
        self.output_window.raise_()
        self.output_window.activateWindow()
        
        # Keep input field enabled state synchronized
        self.output_window.set_input_enabled(self.process_manager.is_running())
    
    def clear_output(self):
        """Clear both output terminals"""
        self.output_text.clear()
        self.output_window.output_terminal.clear()
    
    def show_help(self):
        """Show the help window"""
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()


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