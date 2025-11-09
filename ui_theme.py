"""
Professional UI Theme for Viscum
Provides colors, styles, and helper functions for a polished interface
"""

import tkinter as tk
from tkinter import ttk

class ViscumTheme:
    """Professional color scheme and styling for Viscum GUI"""

    # Color Palette (Scientific Blue/Green theme)
    PRIMARY = "#2C3E50"      # Dark blue-gray
    SECONDARY = "#3498DB"    # Bright blue
    SUCCESS = "#27AE60"      # Green
    WARNING = "#F39C12"      # Orange
    ERROR = "#E74C3C"        # Red
    INFO = "#3498DB"         # Blue

    # Backgrounds
    BG_LIGHT = "#ECF0F1"     # Light gray
    BG_WHITE = "#FFFFFF"     # White
    BG_DARK = "#34495E"      # Dark gray

    # Text
    TEXT_DARK = "#2C3E50"    # Dark blue-gray
    TEXT_LIGHT = "#7F8C8D"   # Medium gray
    TEXT_WHITE = "#FFFFFF"   # White

    # Borders
    BORDER_LIGHT = "#BDC3C7" # Light border
    BORDER_DARK = "#95A5A6"  # Darker border

    # Status colors
    STATUS_READY = SUCCESS
    STATUS_RUNNING = WARNING
    STATUS_ERROR = ERROR
    STATUS_INFO = INFO

    @staticmethod
    def configure_style():
        """Configure ttk styles for the application"""
        style = ttk.Style()

        # Use 'clam' theme as base for better customization
        try:
            style.theme_use('clam')
        except:
            pass  # Fall back to default theme if clam not available

        # Configure LabelFrame
        style.configure(
            "Viscum.TLabelframe",
            background=ViscumTheme.BG_WHITE,
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            "Viscum.TLabelframe.Label",
            background=ViscumTheme.BG_WHITE,
            foreground=ViscumTheme.PRIMARY,
            font=('Segoe UI', 11, 'bold')  # Increased from 10 to 11
        )

        # Configure Buttons
        style.configure(
            "Viscum.TButton",
            background=ViscumTheme.SECONDARY,
            foreground=ViscumTheme.TEXT_WHITE,
            borderwidth=0,
            focuscolor='none',
            font=('Segoe UI', 11)  # Increased from 10 to 11
        )
        style.map(
            "Viscum.TButton",
            background=[('active', ViscumTheme.PRIMARY), ('disabled', ViscumTheme.BORDER_LIGHT)],
            foreground=[('disabled', ViscumTheme.TEXT_LIGHT)]
        )

        # Primary action button (Run, Browse, etc.)
        style.configure(
            "Primary.TButton",
            background=ViscumTheme.SUCCESS,
            foreground=ViscumTheme.TEXT_WHITE,
            font=('Segoe UI', 12, 'bold'),  # Increased from 11 to 12
            padding=8
        )
        style.map(
            "Primary.TButton",
            background=[('active', '#229954'), ('disabled', ViscumTheme.BORDER_LIGHT)]
        )

        # Configure Entry fields
        style.configure(
            "Viscum.TEntry",
            fieldbackground=ViscumTheme.BG_WHITE,
            borderwidth=1,
            relief="solid",
            font=('Segoe UI', 11)  # Added font size
        )

        # Configure Labels
        style.configure(
            "Viscum.TLabel",
            background=ViscumTheme.BG_WHITE,
            foreground=ViscumTheme.TEXT_DARK,
            font=('Segoe UI', 11)  # Increased from 10 to 11
        )

        style.configure(
            "Header.TLabel",
            background=ViscumTheme.BG_WHITE,
            foreground=ViscumTheme.PRIMARY,
            font=('Segoe UI', 14, 'bold')  # Increased from 12 to 14
        )

        # Status labels
        style.configure(
            "Status.TLabel",
            background=ViscumTheme.BG_LIGHT,
            foreground=ViscumTheme.TEXT_DARK,
            font=('Segoe UI', 11),  # Increased from 10 to 11
            padding=5,
            relief="solid",
            borderwidth=1
        )

        # Configure Progressbar
        style.configure(
            "Viscum.Horizontal.TProgressbar",
            background=ViscumTheme.SUCCESS,
            troughcolor=ViscumTheme.BG_LIGHT,
            borderwidth=0,
            thickness=20
        )

    @staticmethod
    def create_section_header(parent, text):
        """Create a styled section header"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(10, 5))

        # Header label with icon
        label = ttk.Label(
            frame,
            text=text,
            style="Header.TLabel"
        )
        label.pack(side=tk.LEFT, padx=5)

        # Separator line
        separator = ttk.Separator(frame, orient='horizontal')
        separator.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        return frame

    @staticmethod
    def create_styled_frame(parent, text=None, padding=10):
        """Create a styled label frame"""
        if text:
            frame = ttk.LabelFrame(
                parent,
                text=text,
                style="Viscum.TLabelframe",
                padding=padding
            )
        else:
            frame = ttk.Frame(parent, style="Viscum.TFrame")
        return frame

    @staticmethod
    def create_primary_button(parent, text, command=None):
        """Create a primary action button"""
        btn = ttk.Button(
            parent,
            text=text,
            command=command,
            style="Primary.TButton"
        )
        return btn

    @staticmethod
    def create_button(parent, text, command=None):
        """Create a standard button"""
        btn = ttk.Button(
            parent,
            text=text,
            command=command,
            style="Viscum.TButton"
        )
        return btn

    @staticmethod
    def validate_entry(entry_widget, is_valid):
        """Apply visual validation feedback to entry widget"""
        if is_valid:
            entry_widget.configure(style="Valid.TEntry")
        else:
            entry_widget.configure(style="Invalid.TEntry")

    @staticmethod
    def configure_validation_styles():
        """Configure styles for input validation"""
        style = ttk.Style()

        style.configure(
            "Valid.TEntry",
            fieldbackground="#D5F4E6",  # Light green
            bordercolor=ViscumTheme.SUCCESS,
            borderwidth=2
        )

        style.configure(
            "Invalid.TEntry",
            fieldbackground="#FADBD8",  # Light red
            bordercolor=ViscumTheme.ERROR,
            borderwidth=2
        )

        style.configure(
            "Neutral.TEntry",
            fieldbackground=ViscumTheme.BG_WHITE,
            bordercolor=ViscumTheme.BORDER_LIGHT,
            borderwidth=1
        )


def apply_theme(root):
    """Apply the Viscum theme to the root window and configure all styles"""
    # Set window background
    root.configure(bg=ViscumTheme.BG_LIGHT)

    # Configure all ttk styles
    ViscumTheme.configure_style()
    ViscumTheme.configure_validation_styles()

    # Set default font for all widgets - larger and better font
    default_font = ('Segoe UI', 11)
    root.option_add('*Font', default_font)

    return ViscumTheme
