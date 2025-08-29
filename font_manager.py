#!/usr/bin/env python3
"""
Font Manager for Python GUI Menu Application
Handles font detection and provides robust cross-platform font fallbacks
"""

import os
import sys
import platform
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtCore import QStandardPaths

class FontManager:
    """Manages font detection and provides cross-platform font fallbacks"""
    
    def __init__(self):
        self.font_db = QFontDatabase()
        self.loaded_fonts = {}
        
        # Platform-specific monospace font stacks
        self.platform_fonts = {
            'Windows': [
                "Consolas",
                "Lucida Console", 
                "Courier New",
                "monospace"
            ],
            'Darwin': [  # macOS
                "SF Mono",
                "Monaco", 
                "Menlo",
                "Courier New",
                "monospace"
            ],
            'Linux': [
                "DejaVu Sans Mono",
                "Liberation Mono",
                "Ubuntu Mono",
                "Noto Sans Mono",
                "Droid Sans Mono",
                "Courier New",
                "monospace"
            ]
        }
        
        # Universal fallback stack
        self.universal_monospace_stack = [
            "DejaVu Sans Mono",
            "Liberation Mono",
            "Consolas",
            "SF Mono",
            "Monaco",
            "Menlo", 
            "Ubuntu Mono",
            "Noto Sans Mono",
            "Droid Sans Mono",
            "Lucida Console",
            "Courier New",
            "Courier",
            "monospace",
            "serif"  # Last resort
        ]
        
        # Get platform-specific fonts first, then universal
        current_platform = platform.system()
        platform_fonts = self.platform_fonts.get(current_platform, [])
        
        # Combine platform-specific + universal (removing duplicates)
        self.monospace_font_stack = []
        seen = set()
        for font in platform_fonts + self.universal_monospace_stack:
            if font not in seen:
                self.monospace_font_stack.append(font)
                seen.add(font)
    
    def get_resource_path(self, relative_path):
        """Get the absolute path to a resource file"""
        if hasattr(sys, '_MEIPASS'):
            # Running from PyInstaller bundle
            return os.path.join(sys._MEIPASS, relative_path)
        else:
            # Running from source
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    
    def detect_best_monospace_font(self):
        """Detect the best available monospace font on this system"""
        # Check available fonts and find the best match
        available_families = set(self.font_db.families())
        
        for font_family in self.monospace_font_stack:
            if font_family in available_families:
                # Verify it's actually monospace
                font = QFont(font_family)
                if font.fixedPitch() or self._is_likely_monospace(font_family):
                    return font_family
        
        # If no specific font found, return the first available from our stack
        for font_family in self.monospace_font_stack:
            if font_family in available_families:
                return font_family
        
        return "Courier"  # Ultimate fallback
    
    def _is_likely_monospace(self, font_family):
        """Check if a font family is likely to be monospace"""
        monospace_indicators = [
            'mono', 'console', 'terminal', 'fixed', 'typewriter', 'courier'
        ]
        font_lower = font_family.lower()
        return any(indicator in font_lower for indicator in monospace_indicators)
    
    def get_monospace_font(self, size=10, weight=QFont.Normal):
        """Get the best available monospace font"""
        best_family = self.detect_best_monospace_font()
        font = QFont(best_family, size, weight)
        
        # Ensure it behaves as monospace
        font.setStyleHint(QFont.TypeWriter)
        font.setFixedPitch(True)
        
        return font
    
    def get_monospace_font_css(self, size=None):
        """Get CSS font-family stack for monospace fonts"""
        css_stack = []
        available_families = set(self.font_db.families())
        
        # Only add fonts that actually exist on this system
        for family in self.monospace_font_stack:
            if family in available_families:
                # Escape font names with spaces  
                if ' ' in family:
                    css_stack.append(f'"{family}"')
                else:
                    css_stack.append(family)
        
        # If no specific fonts were found, add some safe defaults
        if not css_stack:
            css_stack.extend(['Courier New', 'Courier'])
        
        # Add generic fallbacks 
        css_stack.append('monospace')
        
        font_family = f"font-family: {', '.join(css_stack)};"
        
        if size:
            return f"{font_family} font-size: {size}px;"
        return font_family
    
    def list_available_fonts(self):
        """List all available fonts for debugging"""
        families = self.font_db.families()
        monospace_families = []
        
        for family in families:
            font = QFont(family)
            if font.fixedPitch() or 'mono' in family.lower() or family in self.monospace_font_stack:
                monospace_families.append(family)
        
        return {
            'all_families': sorted(families),
            'monospace_families': sorted(monospace_families),
            'loaded_fonts': self.loaded_fonts
        }

# Global font manager instance
_font_manager = None

def get_font_manager():
    """Get the global font manager instance"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager
