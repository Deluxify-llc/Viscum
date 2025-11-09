"""
Tooltip helper for tkinter widgets

Provides easy-to-use tooltips that appear on hover
"""

import tkinter as tk

class ToolTip:
    """
    Create a tooltip for a given widget

    Usage:
        button = ttk.Button(parent, text="Click me")
        ToolTip(button, "This button does something cool")
    """

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

        # Bind hover events
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    def enter(self, event=None):
        """Show tooltip on mouse enter"""
        self.schedule()

    def leave(self, event=None):
        """Hide tooltip on mouse leave"""
        self.unschedule()
        self.hidetip()

    def schedule(self):
        """Schedule tooltip to appear after delay"""
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)  # 500ms delay

    def unschedule(self):
        """Cancel scheduled tooltip"""
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self):
        """Display the tooltip"""
        if self.tipwindow or not self.text:
            return

        # Position tooltip near the widget
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Create tooltip window
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")

        # Style the tooltip
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",  # Light yellow
            foreground="#000000",  # Black text
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 10, "normal"),
            padx=10,
            pady=6,
            wraplength=350  # Wrap long text
        )
        label.pack()

    def hidetip(self):
        """Hide the tooltip"""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    """
    Convenience function to create a tooltip

    Args:
        widget: tkinter widget
        text: tooltip text

    Returns:
        ToolTip instance
    """
    return ToolTip(widget, text)
