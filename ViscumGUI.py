#!/usr/bin/env python3
# GUI for Viscum ball tracker

import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os
from translations import Translator
from tooltip_helper import create_tooltip
from ui_theme import apply_theme, ViscumTheme

class ViscumGUI:
    def __init__(self, root, language=None):
        self.root = root

        # Apply professional theme
        self.theme = apply_theme(root)

        # Initialize translator (auto-detects system language if not specified)
        self.t = Translator(language)

        self.root.title(self.t['window_title'])
        self.root.geometry("1400x950")  # Larger window to show all controls without scrolling

        # tkinter variables
        self.video_path = tk.StringVar()
        self.roi_x1 = tk.IntVar(value=1000)
        self.roi_y1 = tk.IntVar(value=1803)
        self.roi_x2 = tk.IntVar(value=1200)
        self.roi_y2 = tk.IntVar(value=2492)
        self.start_frame = tk.IntVar(value=80)
        self.end_frame = tk.IntVar(value=95)

        self.ball_diameter_mm = tk.DoubleVar(value=3.0)
        self.ball_density = tk.DoubleVar(value=880.0)
        self.liquid_density = tk.DoubleVar(value=872.0)
        self.gravity = tk.DoubleVar(value=9.79)

        # video stuff
        self.cap = None
        self.current_frame = None
        self.current_frame_num = 0
        self.fps = 0
        self.total_frames = 0
        self.display_scale = 1.0

        self.selecting_roi = False
        self.roi_start = None
        self.updating_frame = False

        # Track results data
        self.results_data = None
        self.full_output_data = None

        self.setup_ui()

        # Initialize button states
        self.update_button_states()

    def setup_ui(self):
        # Create tabbed interface with 2 tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Main (Setup + Preview side-by-side)
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text=self.t.get('tab_main') or 'Main')
        self.setup_main_tab()

        # Tab 2: Results & Messages (initially disabled)
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text=self.t.get('tab_results') or 'Results & Messages', state='disabled')
        self.setup_results_tab()

    def setup_main_tab(self):
        """Setup Tab 1: Main (Setup + Preview side-by-side)"""
        parent = self.main_tab

        # Use PanedWindow for resizable split
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left pane: Setup & Configuration (scrollable)
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        self.setup_setup_controls(left_frame)

        # Right pane: Preview & Navigation
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)  # Give more weight to preview
        self.setup_preview_controls(right_frame)

    def setup_setup_controls(self, parent):
        """Setup left side: Setup & Configuration controls"""
        # make it scrollable
        canvas = tk.Canvas(parent, width=350)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # video selection section
        video_frame = ViscumTheme.create_styled_frame(scrollable_frame, text=self.t['section_video'], padding=15)
        video_frame.pack(fill=tk.X, padx=5, pady=5)

        self.browse_btn = ViscumTheme.create_primary_button(video_frame, text=self.t['btn_browse'], command=self.browse_video)
        self.browse_btn.pack(fill=tk.X, pady=2)
        create_tooltip(self.browse_btn, self.t['tooltip_browse'])

        ttk.Label(video_frame, textvariable=self.video_path, wraplength=300, foreground="blue").pack(fill=tk.X, pady=2)

        self.video_info_label = ttk.Label(video_frame, text=self.t['status_no_video'], foreground="gray")
        self.video_info_label.pack(fill=tk.X, pady=2)

        # ROI selection
        roi_frame = ViscumTheme.create_styled_frame(scrollable_frame, text=self.t['section_roi'], padding=15)
        roi_frame.pack(fill=tk.X, padx=5, pady=5)

        self.select_roi_btn = ViscumTheme.create_button(roi_frame, text=self.t['btn_select_roi'], command=self.select_roi_interactive)
        self.select_roi_btn.pack(fill=tk.X, pady=2)
        create_tooltip(self.select_roi_btn, self.t['tooltip_select_roi'])

        roi_grid = ttk.Frame(roi_frame)
        roi_grid.pack(fill=tk.X, pady=5)

        x1_label = ttk.Label(roi_grid, text=self.t['lbl_x1'])
        x1_label.grid(row=0, column=0, sticky=tk.W, padx=2)
        create_tooltip(x1_label, self.t['tooltip_roi_x1'])
        self.x1_entry = ttk.Entry(roi_grid, textvariable=self.roi_x1, width=8)
        self.x1_entry.grid(row=0, column=1, padx=2)
        create_tooltip(self.x1_entry, self.t['tooltip_roi_x1'])

        y1_label = ttk.Label(roi_grid, text=self.t['lbl_y1'])
        y1_label.grid(row=0, column=2, sticky=tk.W, padx=2)
        create_tooltip(y1_label, self.t['tooltip_roi_y1'])
        self.y1_entry = ttk.Entry(roi_grid, textvariable=self.roi_y1, width=8)
        self.y1_entry.grid(row=0, column=3, padx=2)
        create_tooltip(self.y1_entry, self.t['tooltip_roi_y1'])

        x2_label = ttk.Label(roi_grid, text=self.t['lbl_x2'])
        x2_label.grid(row=1, column=0, sticky=tk.W, padx=2)
        create_tooltip(x2_label, self.t['tooltip_roi_x2'])
        self.x2_entry = ttk.Entry(roi_grid, textvariable=self.roi_x2, width=8)
        self.x2_entry.grid(row=1, column=1, padx=2)
        create_tooltip(self.x2_entry, self.t['tooltip_roi_x2'])

        y2_label = ttk.Label(roi_grid, text=self.t['lbl_y2'])
        y2_label.grid(row=1, column=2, sticky=tk.W, padx=2)
        create_tooltip(y2_label, self.t['tooltip_roi_y2'])
        self.y2_entry = ttk.Entry(roi_grid, textvariable=self.roi_y2, width=8)
        self.y2_entry.grid(row=1, column=3, padx=2)
        create_tooltip(self.y2_entry, self.t['tooltip_roi_y2'])

        # Frame Range
        frame_frame = ViscumTheme.create_styled_frame(scrollable_frame, text=self.t['section_frames'], padding=15)
        frame_frame.pack(fill=tk.X, padx=5, pady=5)

        frame_grid = ttk.Frame(frame_frame)
        frame_grid.pack(fill=tk.X)

        start_frame_label = ttk.Label(frame_grid, text=self.t['lbl_start_frame'])
        start_frame_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(start_frame_label, self.t['tooltip_start_frame'])
        self.start_frame_entry = ttk.Entry(frame_grid, textvariable=self.start_frame, width=10)
        self.start_frame_entry.grid(row=0, column=1, padx=2, pady=2)
        create_tooltip(self.start_frame_entry, self.t['tooltip_start_frame'])

        end_frame_label = ttk.Label(frame_grid, text=self.t['lbl_end_frame'])
        end_frame_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(end_frame_label, self.t['tooltip_end_frame'])
        self.end_frame_entry = ttk.Entry(frame_grid, textvariable=self.end_frame, width=10)
        self.end_frame_entry.grid(row=1, column=1, padx=2, pady=2)
        create_tooltip(self.end_frame_entry, self.t['tooltip_end_frame'])

        self.preview_btn = ViscumTheme.create_button(frame_frame, text=self.t['btn_preview'], command=self.preview_frame)
        self.preview_btn.pack(fill=tk.X, pady=5)
        create_tooltip(self.preview_btn, self.t['tooltip_preview'])

        # Ball Properties
        ball_frame = ViscumTheme.create_styled_frame(scrollable_frame, text=self.t['section_ball'], padding=15)
        ball_frame.pack(fill=tk.X, padx=5, pady=5)

        ball_grid = ttk.Frame(ball_frame)
        ball_grid.pack(fill=tk.X)

        diameter_label = ttk.Label(ball_grid, text=self.t['lbl_diameter'])
        diameter_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(diameter_label, self.t['tooltip_diameter'])
        self.diameter_entry = ttk.Entry(ball_grid, textvariable=self.ball_diameter_mm, width=10)
        self.diameter_entry.grid(row=0, column=1, padx=2, pady=2)
        create_tooltip(self.diameter_entry, self.t['tooltip_diameter'])

        ball_density_label = ttk.Label(ball_grid, text=self.t['lbl_ball_density'])
        ball_density_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(ball_density_label, self.t['tooltip_ball_density'])
        self.ball_density_entry = ttk.Entry(ball_grid, textvariable=self.ball_density, width=10)
        self.ball_density_entry.grid(row=1, column=1, padx=2, pady=2)
        create_tooltip(self.ball_density_entry, self.t['tooltip_ball_density'])

        # Liquid Properties
        liquid_frame = ViscumTheme.create_styled_frame(scrollable_frame, text=self.t['section_liquid'], padding=15)
        liquid_frame.pack(fill=tk.X, padx=5, pady=5)

        liquid_grid = ttk.Frame(liquid_frame)
        liquid_grid.pack(fill=tk.X)

        liquid_density_label = ttk.Label(liquid_grid, text=self.t['lbl_liquid_density'])
        liquid_density_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(liquid_density_label, self.t['tooltip_liquid_density'])
        self.liquid_density_entry = ttk.Entry(liquid_grid, textvariable=self.liquid_density, width=10)
        self.liquid_density_entry.grid(row=0, column=1, padx=2, pady=2)
        create_tooltip(self.liquid_density_entry, self.t['tooltip_liquid_density'])

        gravity_label = ttk.Label(liquid_grid, text=self.t['lbl_gravity'])
        gravity_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(gravity_label, self.t['tooltip_gravity'])
        self.gravity_entry = ttk.Entry(liquid_grid, textvariable=self.gravity, width=10)
        self.gravity_entry.grid(row=1, column=1, padx=2, pady=2)
        create_tooltip(self.gravity_entry, self.t['tooltip_gravity'])

        # calibration test option
        calib_frame = ViscumTheme.create_styled_frame(scrollable_frame, text=self.t['section_calibration'], padding=15)
        calib_frame.pack(fill=tk.X, padx=5, pady=5)

        self.is_calibration = tk.BooleanVar(value=False)
        calib_checkbox = ttk.Checkbutton(calib_frame, text=self.t['chk_calibration'],
                       variable=self.is_calibration,
                       command=self.toggle_calibration)
        calib_checkbox.pack(anchor=tk.W, pady=2)
        create_tooltip(calib_checkbox, self.t['tooltip_calibration'])

        self.calib_inputs = ttk.Frame(calib_frame)

        temp_label = ttk.Label(self.calib_inputs, text=self.t['lbl_temperature'])
        temp_label.grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(temp_label, self.t['tooltip_temperature'])
        self.temp = tk.DoubleVar(value=25.0)
        self.temp_entry = ttk.Entry(self.calib_inputs, textvariable=self.temp, width=10)
        self.temp_entry.grid(row=0, column=1, padx=2, pady=2)
        create_tooltip(self.temp_entry, self.t['tooltip_temperature'])

        visc_40_label = ttk.Label(self.calib_inputs, text=self.t['lbl_visc_40'])
        visc_40_label.grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(visc_40_label, self.t['tooltip_visc_40'])
        self.visc_40 = tk.DoubleVar(value=0.0)
        self.visc_40_entry = ttk.Entry(self.calib_inputs, textvariable=self.visc_40, width=10)
        self.visc_40_entry.grid(row=1, column=1, padx=2, pady=2)
        create_tooltip(self.visc_40_entry, self.t['tooltip_visc_40'])

        visc_100_label = ttk.Label(self.calib_inputs, text=self.t['lbl_visc_100'])
        visc_100_label.grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        create_tooltip(visc_100_label, self.t['tooltip_visc_100'])
        self.visc_100 = tk.DoubleVar(value=0.0)
        self.visc_100_entry = ttk.Entry(self.calib_inputs, textvariable=self.visc_100, width=10)
        self.visc_100_entry.grid(row=2, column=1, padx=2, pady=2)
        create_tooltip(self.visc_100_entry, self.t['tooltip_visc_100'])

        # run button
        run_frame = ttk.Frame(scrollable_frame, padding=10)
        run_frame.pack(fill=tk.X, padx=5, pady=10)

        self.run_button = ViscumTheme.create_primary_button(run_frame, text=self.t['btn_run'], command=self.run_tracking)
        self.run_button.pack(fill=tk.X, pady=2)
        create_tooltip(self.run_button, self.t['tooltip_run'])

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(run_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        # Styled status label with rounded background
        status_frame = ttk.Frame(run_frame, style="Viscum.TFrame")
        status_frame.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(
            status_frame,
            text=self.t['status_ready'],
            foreground="white",
            background=ViscumTheme.SUCCESS,
            font=('Segoe UI', 12, 'bold'),
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=8
        )
        self.status_label.pack(fill=tk.X)

        # Help button for confidence explanation
        help_frame = ttk.Frame(run_frame, style="Viscum.TFrame")
        help_frame.pack(fill=tk.X, pady=5)

        help_btn = ViscumTheme.create_button(help_frame, text=self.t['help_confidence'] + " (?)",
                                             command=self.show_confidence_help)
        help_btn.pack(side=tk.LEFT, padx=5)
        create_tooltip(help_btn, "Click to learn about confidence scores in tracking results")

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_results_tab(self):
        """Setup Tab 2: Results & Messages"""
        parent = self.results_tab

        # Main scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.results_scrollable_frame = ttk.Frame(canvas)

        self.results_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.results_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Messages container at top (initially hidden)
        self.messages_frame = ttk.Frame(self.results_scrollable_frame)
        self.messages_frame.pack(fill=tk.X, padx=10, pady=10)

        # Results container below messages
        self.results_content_frame = ttk.Frame(self.results_scrollable_frame)
        self.results_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Placeholder text
        ttk.Label(self.results_content_frame,
                 text=self.t.get('results_placeholder') or 'Results will appear here after tracking completes',
                 font=('Segoe UI', 14),
                 foreground='gray').pack(pady=100)

    def show_message(self, msg_type, title, message, callback=None):
        """
        Show a message in the Results tab instead of a popup
        msg_type: 'error', 'warning', 'info', 'success', 'question'
        callback: optional callback for 'question' type with yes/no buttons
        Returns: True/False for question type, None otherwise
        """
        # Enable and switch to Results tab
        self.notebook.tab(1, state='normal')
        self.notebook.select(1)

        # Clear previous messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()

        # Color mapping based on message type
        color_map = {
            'error': ViscumTheme.ERROR,
            'warning': ViscumTheme.WARNING,
            'info': ViscumTheme.INFO,
            'success': ViscumTheme.SUCCESS,
            'question': ViscumTheme.INFO
        }
        bg_color = color_map.get(msg_type, ViscumTheme.INFO)

        # Create message container
        msg_container = ttk.Frame(self.messages_frame, relief=tk.RIDGE, borderwidth=2)
        msg_container.pack(fill=tk.X, pady=5)

        # Title label
        title_label = tk.Label(
            msg_container,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            foreground='white',
            background=bg_color,
            anchor=tk.W,
            padx=15,
            pady=10
        )
        title_label.pack(fill=tk.X)

        # Message label
        msg_label = ttk.Label(
            msg_container,
            text=message,
            font=('Segoe UI', 11),
            wraplength=700,
            justify=tk.LEFT
        )
        msg_label.pack(fill=tk.X, padx=15, pady=10)

        # For question type, add Yes/No buttons
        if msg_type == 'question' and callback:
            btn_frame = ttk.Frame(msg_container)
            btn_frame.pack(fill=tk.X, padx=15, pady=10)

            result_holder = {'value': False}

            def on_yes():
                result_holder['value'] = True
                msg_container.destroy()
                if callback:
                    callback(True)

            def on_no():
                result_holder['value'] = False
                msg_container.destroy()
                if callback:
                    callback(False)

            yes_btn = ViscumTheme.create_primary_button(btn_frame, text="Yes", command=on_yes)
            yes_btn.pack(side=tk.LEFT, padx=5)

            no_btn = ViscumTheme.create_button(btn_frame, text="No", command=on_no)
            no_btn.pack(side=tk.LEFT, padx=5)

            return result_holder
        else:
            # Add close button for other message types
            close_btn = ViscumTheme.create_button(msg_container, text="Close",
                                                  command=msg_container.destroy)
            close_btn.pack(pady=10)

        return None

    def toggle_calibration(self):
        if self.is_calibration.get():
            self.calib_inputs.pack(fill=tk.X, pady=5)
        else:
            self.calib_inputs.pack_forget()

    def show_confidence_help(self):
        """Display a help dialog explaining confidence scores"""
        help_window = tk.Toplevel(self.root)
        help_window.title(self.t['confidence_title'])
        help_window.geometry("600x400")
        help_window.resizable(True, True)

        # Center the window
        help_window.transient(self.root)
        help_window.grab_set()

        # Main frame with padding
        main_frame = ttk.Frame(help_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text=self.t['confidence_title'],
                               font=('Segoe UI', 16, 'bold'),
                               foreground=ViscumTheme.PRIMARY)
        title_label.pack(pady=(0, 15))

        # Introduction text
        intro_text = tk.Text(main_frame, wrap=tk.WORD, height=2, font=('Segoe UI', 11),
                            relief=tk.FLAT, background=ViscumTheme.BG_LIGHT)
        intro_text.insert('1.0', self.t['confidence_intro'])
        intro_text.config(state=tk.DISABLED)
        intro_text.pack(fill=tk.X, pady=10)

        # Confidence levels frame
        levels_frame = ttk.LabelFrame(main_frame, text="Confidence Levels", padding=15)
        levels_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # High confidence
        high_frame = ttk.Frame(levels_frame)
        high_frame.pack(fill=tk.X, pady=5)
        high_indicator = tk.Label(high_frame, text="●", font=('Segoe UI', 20),
                                 foreground='green', background=ViscumTheme.BG_WHITE)
        high_indicator.pack(side=tk.LEFT, padx=5)
        high_label = ttk.Label(high_frame, text=self.t['confidence_high'],
                              font=('Segoe UI', 11))
        high_label.pack(side=tk.LEFT, padx=5)

        # Medium confidence
        med_frame = ttk.Frame(levels_frame)
        med_frame.pack(fill=tk.X, pady=5)
        med_indicator = tk.Label(med_frame, text="●", font=('Segoe UI', 20),
                                foreground='#F39C12', background=ViscumTheme.BG_WHITE)
        med_indicator.pack(side=tk.LEFT, padx=5)
        med_label = ttk.Label(med_frame, text=self.t['confidence_medium'],
                             font=('Segoe UI', 11))
        med_label.pack(side=tk.LEFT, padx=5)

        # Low confidence
        low_frame = ttk.Frame(levels_frame)
        low_frame.pack(fill=tk.X, pady=5)
        low_indicator = tk.Label(low_frame, text="●", font=('Segoe UI', 20),
                                foreground='red', background=ViscumTheme.BG_WHITE)
        low_indicator.pack(side=tk.LEFT, padx=5)
        low_label = ttk.Label(low_frame, text=self.t['confidence_low'],
                             font=('Segoe UI', 11))
        low_label.pack(side=tk.LEFT, padx=5)

        # Recommendation text
        rec_frame = ttk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        rec_frame.pack(fill=tk.X, pady=10)
        rec_label = ttk.Label(rec_frame, text=self.t['confidence_avg'],
                             font=('Segoe UI', 11, 'bold'),
                             foreground=ViscumTheme.INFO,
                             background=ViscumTheme.BG_WHITE)
        rec_label.pack(padx=10, pady=8)

        # Note text
        note_text = tk.Text(main_frame, wrap=tk.WORD, height=2, font=('Segoe UI', 10),
                           relief=tk.FLAT, background=ViscumTheme.BG_LIGHT,
                           foreground=ViscumTheme.TEXT_LIGHT)
        note_text.insert('1.0', self.t['confidence_note'])
        note_text.config(state=tk.DISABLED)
        note_text.pack(fill=tk.X, pady=5)

        # Close button
        close_btn = ViscumTheme.create_primary_button(main_frame, text="Close",
                                                      command=help_window.destroy)
        close_btn.pack(pady=10)

    def update_button_states(self):
        """Enable/disable buttons based on application state"""
        video_loaded = self.cap is not None

        # Enable buttons that require a video
        state = "normal" if video_loaded else "disabled"
        self.select_roi_btn.config(state=state)
        self.select_roi_btn_preview.config(state=state)
        self.preview_btn.config(state=state)
        self.run_button.config(state=state)

    def validate_inputs(self):
        """Validate all input fields and provide visual feedback"""
        all_valid = True

        # Validate ROI coordinates
        try:
            x1, y1, x2, y2 = self.roi_x1.get(), self.roi_y1.get(), self.roi_x2.get(), self.roi_y2.get()
            roi_valid = x2 > x1 and y2 > y1

            for entry in [self.x1_entry, self.y1_entry, self.x2_entry, self.y2_entry]:
                entry.config(style="Valid.TEntry" if roi_valid else "Invalid.TEntry")

            if not roi_valid:
                all_valid = False
        except:
            all_valid = False
            for entry in [self.x1_entry, self.y1_entry, self.x2_entry, self.y2_entry]:
                entry.config(style="Invalid.TEntry")

        # Validate frame range
        try:
            start, end = self.start_frame.get(), self.end_frame.get()
            frames_valid = end > start

            if self.cap:
                frames_valid = frames_valid and start >= 0 and end < self.total_frames

            self.start_frame_entry.config(style="Valid.TEntry" if frames_valid else "Invalid.TEntry")
            self.end_frame_entry.config(style="Valid.TEntry" if frames_valid else "Invalid.TEntry")

            if not frames_valid:
                all_valid = False
        except:
            all_valid = False
            self.start_frame_entry.config(style="Invalid.TEntry")
            self.end_frame_entry.config(style="Invalid.TEntry")

        # Validate ball diameter
        try:
            diameter_valid = self.ball_diameter_mm.get() > 0
            self.diameter_entry.config(style="Valid.TEntry" if diameter_valid else "Invalid.TEntry")
            if not diameter_valid:
                all_valid = False
        except:
            all_valid = False
            self.diameter_entry.config(style="Invalid.TEntry")

        # Validate densities
        try:
            ball_density_valid = self.ball_density.get() > 0
            self.ball_density_entry.config(style="Valid.TEntry" if ball_density_valid else "Invalid.TEntry")
            if not ball_density_valid:
                all_valid = False
        except:
            all_valid = False
            self.ball_density_entry.config(style="Invalid.TEntry")

        try:
            liquid_density_valid = self.liquid_density.get() > 0
            self.liquid_density_entry.config(style="Valid.TEntry" if liquid_density_valid else "Invalid.TEntry")
            if not liquid_density_valid:
                all_valid = False
        except:
            all_valid = False
            self.liquid_density_entry.config(style="Invalid.TEntry")

        try:
            gravity_valid = self.gravity.get() > 0
            self.gravity_entry.config(style="Valid.TEntry" if gravity_valid else "Invalid.TEntry")
            if not gravity_valid:
                all_valid = False
        except:
            all_valid = False
            self.gravity_entry.config(style="Invalid.TEntry")

        # Validate calibration inputs if enabled
        if self.is_calibration.get():
            try:
                temp_valid = True  # Temperature can be any value
                self.temp_entry.config(style="Valid.TEntry" if temp_valid else "Invalid.TEntry")
            except:
                all_valid = False
                self.temp_entry.config(style="Invalid.TEntry")

            try:
                visc_40_valid = self.visc_40.get() > 0
                self.visc_40_entry.config(style="Valid.TEntry" if visc_40_valid else "Invalid.TEntry")
                if not visc_40_valid:
                    all_valid = False
            except:
                all_valid = False
                self.visc_40_entry.config(style="Invalid.TEntry")

            try:
                visc_100_valid = self.visc_100.get() > 0
                self.visc_100_entry.config(style="Valid.TEntry" if visc_100_valid else "Invalid.TEntry")
                if not visc_100_valid:
                    all_valid = False
            except:
                all_valid = False
                self.visc_100_entry.config(style="Invalid.TEntry")

        return all_valid

    def setup_preview_controls(self, parent):
        """Setup right side: Preview & Navigation"""
        # Large preview canvas (takes up most of the tab)
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(preview_frame, bg="black", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # ROI selection tools above navigation
        roi_tools_frame = ttk.Frame(parent)
        roi_tools_frame.pack(fill=tk.X, padx=5, pady=5)

        self.select_roi_btn_preview = ViscumTheme.create_button(roi_tools_frame,
                                                                 text=self.t['btn_select_roi'],
                                                                 command=self.select_roi_interactive)
        self.select_roi_btn_preview.pack(side=tk.LEFT, padx=5)
        create_tooltip(self.select_roi_btn_preview, self.t['tooltip_select_roi'])

        ttk.Label(roi_tools_frame,
                 text=self.t.get('roi_hint') or 'Click and drag on video to select ROI').pack(side=tk.LEFT, padx=10)

        # frame controls
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        backward_fast_btn = ViscumTheme.create_button(nav_frame, text="◀◀", command=lambda: self.navigate_frame(-10))
        backward_fast_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(backward_fast_btn, self.t['tooltip_nav_backward_fast'])

        backward_btn = ViscumTheme.create_button(nav_frame, text="◀", command=lambda: self.navigate_frame(-1))
        backward_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(backward_btn, self.t['tooltip_nav_backward'])

        self.frame_scale = ttk.Scale(nav_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_frame_scale)
        self.frame_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        create_tooltip(self.frame_scale, self.t['tooltip_frame_slider'])

        forward_btn = ViscumTheme.create_button(nav_frame, text="▶", command=lambda: self.navigate_frame(1))
        forward_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(forward_btn, self.t['tooltip_nav_forward'])

        forward_fast_btn = ViscumTheme.create_button(nav_frame, text="▶▶", command=lambda: self.navigate_frame(10))
        forward_fast_btn.pack(side=tk.LEFT, padx=2)
        create_tooltip(forward_fast_btn, self.t['tooltip_nav_forward_fast'])

        self.frame_label = ttk.Label(nav_frame, text=self.t.get('lbl_frame', current=0, total=0))
        self.frame_label.pack(side=tk.LEFT, padx=10)

    def browse_video(self):
        filename = filedialog.askopenfilename(
            title=self.t['dialog_select_video'],
            filetypes=[(self.t['dialog_video_files'], "*.mp4 *.avi *.mov *.mkv"), (self.t['dialog_all_files'], "*.*")]
        )

        if filename:
            self.video_path.set(filename)
            self.load_video(filename)

    def load_video(self, path):
        # Show loading cursor
        self.root.config(cursor="watch")
        self.root.update()

        try:
            if self.cap:
                self.cap.release()

            self.cap = cv2.VideoCapture(path)

            if not self.cap.isOpened():
                self.show_message('error', self.t['error_title'], self.t['error_open_video'])
                return

            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

            self.video_info_label.config(
                text=self.t.get('status_video_loaded', fps=self.fps, frames=self.total_frames),
                foreground="green"
            )

            self.frame_scale.config(to=self.total_frames - 1)
            self.end_frame.set(min(self.total_frames - 1, self.end_frame.get()))

            # Load first frame
            self.show_frame(0)

            # Update button states now that video is loaded
            self.update_button_states()

        finally:
            # Restore normal cursor
            self.root.config(cursor="")

    def show_frame(self, frame_num):
        if not self.cap or self.updating_frame:
            return

        self.updating_frame = True

        try:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.cap.read()

            if not ret:
                return

            self.current_frame = frame
            self.current_frame_num = frame_num

            # Draw ROI if defined
            display_frame = frame.copy()
            cv2.rectangle(display_frame,
                         (self.roi_x1.get(), self.roi_y1.get()),
                         (self.roi_x2.get(), self.roi_y2.get()),
                         (0, 255, 0), 2)

            # Convert to PhotoImage
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)

            # Force canvas update to get proper dimensions
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width > 1 and canvas_height > 1:
                h, w = rgb_frame.shape[:2]
                scale = min(canvas_width / w, canvas_height / h)
                new_w = int(w * scale)
                new_h = int(h * scale)

                rgb_frame = cv2.resize(rgb_frame, (new_w, new_h))
                self.display_scale = scale
            else:
                self.display_scale = 1.0

            img = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(image=img)

            # Center the image in the canvas
            self.canvas.delete("all")
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            self.canvas.create_image(center_x, center_y, anchor=tk.CENTER, image=photo)
            self.canvas.image = photo  # Keep reference

            self.frame_label.config(text=self.t.get('lbl_frame', current=frame_num, total=self.total_frames-1))
            self.frame_scale.set(frame_num)
        finally:
            self.updating_frame = False

    def on_canvas_resize(self, event):
        """Re-scale video when canvas is resized"""
        if self.current_frame is not None:
            self.show_frame(self.current_frame_num)

    def navigate_frame(self, delta):
        if not self.cap:
            return
        new_frame = max(0, min(self.total_frames - 1, self.current_frame_num + delta))
        self.show_frame(new_frame)

    def on_frame_scale(self, value):
        frame_num = int(float(value))
        self.show_frame(frame_num)

    def preview_frame(self):
        if not self.cap:
            self.show_message('warning', self.t['warn_title'], self.t['warn_no_video'])
            return
        self.show_frame(self.start_frame.get())

    def select_roi_interactive(self):
        if not self.cap:
            self.show_message('warning', self.t['warn_title'], self.t['warn_no_video'])
            return

        self.selecting_roi = True
        self.status_label.config(
            text=self.t['status_roi_select'],
            foreground="white",
            background=ViscumTheme.INFO
        )

    def on_canvas_click(self, event):
        if self.selecting_roi and self.current_frame is not None and self.display_scale > 0:
            # Get canvas center offset
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            h, w = self.current_frame.shape[:2]
            scaled_w = int(w * self.display_scale)
            scaled_h = int(h * self.display_scale)

            offset_x = (canvas_width - scaled_w) // 2
            offset_y = (canvas_height - scaled_h) // 2

            # Convert canvas coordinates to image coordinates
            x = int((event.x - offset_x) / self.display_scale)
            y = int((event.y - offset_y) / self.display_scale)
            self.roi_start = (x, y)

    def on_canvas_drag(self, event):
        if self.selecting_roi and self.roi_start and self.display_scale > 0:
            # Get canvas center offset
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            h, w = self.current_frame.shape[:2]
            scaled_w = int(w * self.display_scale)
            scaled_h = int(h * self.display_scale)

            offset_x = (canvas_width - scaled_w) // 2
            offset_y = (canvas_height - scaled_h) // 2

            # Convert canvas coordinates to image coordinates
            x = int((event.x - offset_x) / self.display_scale)
            y = int((event.y - offset_y) / self.display_scale)

            self.roi_x1.set(min(self.roi_start[0], x))
            self.roi_y1.set(min(self.roi_start[1], y))
            self.roi_x2.set(max(self.roi_start[0], x))
            self.roi_y2.set(max(self.roi_start[1], y))

            self.show_frame(self.current_frame_num)

    def on_canvas_release(self, event):
        if self.selecting_roi:
            self.selecting_roi = False
            self.roi_start = None
            self.status_label.config(
                text=self.t['status_roi_selected'],
                foreground="white",
                background=ViscumTheme.SUCCESS
            )

    def run_tracking(self):
        if not self.video_path.get():
            self.show_message('warning', self.t['warn_title'], self.t['warn_select_video'])
            return

        # Validate inputs
        if not self.validate_inputs():
            self.show_message(
                'error',
                self.t['error_title'],
                "Please correct the invalid input fields (shown in red) before running tracking."
            )
            return

        # Confirmation dialog with callback
        def on_confirm(confirmed):
            if confirmed:
                # Run in separate thread
                thread = threading.Thread(target=self.execute_tracking)
                thread.daemon = True
                thread.start()

        self.show_message(
            'question',
            "Confirm Tracking",
            "This may take a few minutes depending on the video length and frame range.\n\nContinue?",
            callback=on_confirm
        )

    def execute_tracking(self):
        self.run_button.config(state="disabled")
        self.status_label.config(
            text=self.t['status_running'],
            foreground="white",
            background=ViscumTheme.WARNING
        )

        # Create parameters file
        params_file = "temp_params.txt"
        with open(params_file, 'w') as f:
            f.write(f"{self.video_path.get()}\n")
            f.write(f"{self.roi_x1.get()}\n")
            f.write(f"{self.roi_y1.get()}\n")
            f.write(f"{self.roi_x2.get()}\n")
            f.write(f"{self.roi_y2.get()}\n")
            f.write(f"{self.start_frame.get()}\n")
            f.write(f"{self.end_frame.get()}\n")
            f.write(f"{self.ball_diameter_mm.get()}\n")
            f.write(f"{self.gravity.get()}\n")
            f.write(f"{self.ball_density.get()}\n")
            f.write(f"{self.liquid_density.get()}\n")

            if self.is_calibration.get():
                f.write("yes\n")
                f.write(f"{self.temp.get()}\n")
                f.write(f"{self.visc_40.get()}\n")
                f.write(f"{self.visc_100.get()}\n")
            else:
                f.write("no\n")

        # Run VideoProcessor
        import subprocess
        import sys
        try:
            result = subprocess.run(
                f'{sys.executable} VideoProcessor.py --save-plots --plots-dir debug_detect < {params_file}',
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )

            self.root.after(0, lambda: self.tracking_complete(result))

        except Exception as e:
            self.root.after(0, lambda: self.tracking_error(str(e)))
        finally:
            if os.path.exists(params_file):
                os.remove(params_file)

    def tracking_complete(self, result):
        self.run_button.config(state="normal")
        self.progress_var.set(100)

        # Show success message with animation
        self.status_label.config(
            text=self.t['status_complete'],
            foreground="white",
            background=ViscumTheme.SUCCESS
        )

        # Parse results from output
        output = result.stdout
        stderr_output = result.stderr

        # Debug: print full output to console
        print("=== VideoProcessor Output (stdout) ===")
        print(output)
        print("=== End Output ===\n")

        if stderr_output:
            print("=== VideoProcessor Errors (stderr) ===")
            print(stderr_output)
            print("=== End Errors ===\n")

        # Extract key results - be specific to avoid matching input prompts
        results = {}
        try:
            for line in output.split('\n'):
                # Use more specific patterns to avoid matching input prompts
                if line.startswith('Average ball diameter'):
                    results['avg_diameter'] = line.split(':', 1)[1].strip()
                    print(f"Parsed avg_diameter: {results['avg_diameter']}")
                elif line.startswith('Final filtered velocity:'):
                    results['velocity'] = line.split(':', 1)[1].strip()
                    print(f"Parsed velocity: {results['velocity']}")
                elif line.startswith('Final mmtopixel:'):
                    results['mm_per_pixel'] = line.split(':', 1)[1].strip()
                    print(f"Parsed mm_per_pixel: {results['mm_per_pixel']}")
                elif line.startswith('Final mm velocity:'):
                    results['mm_velocity'] = line.split(':', 1)[1].strip()
                    print(f"Parsed mm_velocity: {results['mm_velocity']}")
                elif line.startswith('Final Fluid Viscosity:'):
                    results['viscosity'] = line.split(':', 1)[1].strip()
                    print(f"Parsed viscosity: {results['viscosity']}")
                elif line.startswith('Activation Energy (Ea):'):
                    results['activation_energy'] = line.split(':', 1)[1].strip()
                    print(f"Parsed activation_energy: {results['activation_energy']}")
                elif line.startswith('Pre-exponential Factor (A):'):
                    results['pre_exp_factor'] = line.split(':', 1)[1].strip()
                    print(f"Parsed pre_exp_factor: {results['pre_exp_factor']}")
                elif line.startswith('Viscosity at') and '°C:' in line:
                    # Extract everything after the last ':'
                    results['calculated_viscosity'] = line.split(':')[-1].strip()
                    print(f"Parsed calculated_viscosity: {results['calculated_viscosity']}")
                elif line.startswith('Relative error between'):
                    results['error'] = line.split(':', 1)[1].strip()
                    print(f"Parsed error: {results['error']}")
        except Exception as e:
            print(f"Error parsing results: {e}")

        print(f"\nTotal results parsed: {len(results)}")
        print(f"Results keys: {list(results.keys())}\n")

        # Store results data
        self.results_data = results
        self.full_output_data = output

        # Populate and enable Results tab
        self.populate_results_tab(results, output)
        self.notebook.tab(1, state='normal')

        # Switch to Results tab
        self.notebook.select(1)

    def populate_results_tab(self, results, full_output):
        """Populate the Results tab with tracking results"""
        # Clear existing content in results area only (keep messages)
        for widget in self.results_content_frame.winfo_children():
            widget.destroy()

        # Main content frame with padding
        main_frame = ttk.Frame(self.results_content_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text=self.t['results_header'],
                         font=('Segoe UI', 16, 'bold'),
                         foreground=ViscumTheme.PRIMARY)
        title.pack(pady=(0, 15))

        # Results frame
        results_frame = ViscumTheme.create_styled_frame(main_frame, text=self.t['section_calculated'], padding=15)
        results_frame.pack(fill=tk.X, pady=10)

        if results:
            row = 0
            if 'avg_diameter' in results:
                ttk.Label(results_frame, text=self.t['result_avg_diameter'],
                         font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['avg_diameter']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'velocity' in results:
                ttk.Label(results_frame, text=self.t['result_velocity_px'],
                         font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['velocity']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'mm_per_pixel' in results:
                ttk.Label(results_frame, text=self.t['result_mm_per_px'],
                         font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['mm_per_pixel']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'mm_velocity' in results:
                ttk.Label(results_frame, text=self.t['result_velocity_mm'],
                         font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['mm_velocity']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'viscosity' in results:
                ttk.Label(results_frame, text="").grid(row=row, column=0, pady=5)
                row += 1

                # Highlight viscosity result
                visc_frame = ttk.Frame(results_frame, relief=tk.RIDGE, borderwidth=2)
                visc_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)

                tk.Label(visc_frame, text=self.t['result_viscosity'],
                         font=('Segoe UI', 14, 'bold'),
                         foreground='white',
                         background=ViscumTheme.PRIMARY).pack(side=tk.LEFT, padx=10, pady=10)
                tk.Label(visc_frame, text=results['viscosity'],
                         font=('Segoe UI', 14, 'bold'),
                         foreground='white',
                         background=ViscumTheme.SUCCESS).pack(side=tk.LEFT, padx=10, pady=10)
                row += 1

            # Calibration results if present
            if 'calculated_viscosity' in results:
                ttk.Label(results_frame, text="").grid(row=row, column=0, pady=5)
                row += 1

                # Calibration section
                calib_label = ttk.Label(results_frame, text=self.t['section_calib_results'],
                                       font=('Segoe UI', 13, 'bold', 'underline'),
                                       foreground=ViscumTheme.INFO)
                calib_label.grid(row=row, column=0, columnspan=2, pady=5)
                row += 1

                if 'activation_energy' in results:
                    ttk.Label(results_frame, text=self.t['result_activation_energy'],
                             font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=3)
                    ttk.Label(results_frame, text=results['activation_energy']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
                    row += 1

                if 'pre_exp_factor' in results:
                    ttk.Label(results_frame, text=self.t['result_pre_exp'],
                             font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=3)
                    ttk.Label(results_frame, text=results['pre_exp_factor']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
                    row += 1

                ttk.Label(results_frame, text=self.t['result_expected_visc'],
                         font=('Segoe UI', 12, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=3)
                ttk.Label(results_frame, text=results['calculated_viscosity']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
                row += 1

                if 'error' in results:
                    error_val = results['error']

                    # Determine color based on error value
                    try:
                        error_num = float(error_val)
                        color = ViscumTheme.ERROR if error_num > 0.1 else ViscumTheme.SUCCESS
                        # Convert to percentage for display
                        error_percent = f"{error_num * 100:.2f}%"
                    except:
                        color = ViscumTheme.WARNING
                        error_percent = error_val

                    # Highlight error result in a frame
                    error_frame = ttk.Frame(results_frame, relief=tk.RIDGE, borderwidth=2)
                    error_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)

                    tk.Label(error_frame, text=self.t['result_error'],
                             font=('Segoe UI', 13, 'bold'),
                             foreground='white',
                             background=ViscumTheme.INFO).pack(side=tk.LEFT, padx=10, pady=10)
                    tk.Label(error_frame, text=error_percent,
                             font=('Segoe UI', 13, 'bold'),
                             foreground='white',
                             background=color).pack(side=tk.LEFT, padx=10, pady=10)
                    row += 1

        else:
            ttk.Label(results_frame, text=self.t['result_no_parse'],
                     foreground=ViscumTheme.WARNING).pack()

        # Graphs section
        graphs_frame = ViscumTheme.create_styled_frame(main_frame, text=self.t['section_graphs'], padding=15)
        graphs_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Load and display plot images
        plot_files = [
            ('debug_detect/plot_position.png', 'Ball Position vs Time'),
            ('debug_detect/plot_velocity.png', 'Velocity vs Time'),
            ('debug_detect/plot_diameter.png', 'Ball Diameter vs Time'),
            ('debug_detect/plot_confidence.png', 'Tracking Confidence vs Time')
        ]

        for plot_path, plot_title in plot_files:
            if os.path.exists(plot_path):
                try:
                    # Load image
                    img = Image.open(plot_path)
                    # Resize to fit in GUI (max width 800px)
                    max_width = 800
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_size = (max_width, int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)

                    photo = ImageTk.PhotoImage(img)

                    # Create frame for this plot
                    plot_frame = ttk.Frame(graphs_frame)
                    plot_frame.pack(fill=tk.X, pady=10)

                    # Title
                    ttk.Label(plot_frame, text=plot_title,
                             font=('Segoe UI', 12, 'bold'),
                             foreground=ViscumTheme.PRIMARY).pack(pady=5)

                    # Image
                    img_label = tk.Label(plot_frame, image=photo)
                    img_label.image = photo  # Keep reference
                    img_label.pack()

                except Exception as e:
                    print(f"Error loading plot {plot_path}: {e}")

        # Full output
        output_frame = ViscumTheme.create_styled_frame(main_frame, text=self.t['section_full_output'], padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Text widget with scrollbar
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=15,
                             yscrollcommand=scrollbar.set, font=('Courier New', 10))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert('1.0', full_output)
        text_widget.config(state=tk.DISABLED)

        # Save Results button
        save_btn_frame = ttk.Frame(main_frame)
        save_btn_frame.pack(fill=tk.X, pady=10)

        save_btn = ViscumTheme.create_primary_button(save_btn_frame,
                                                     text=self.t.get('btn_save_results') or 'Save Results',
                                                     command=self.save_results)
        save_btn.pack(pady=5)

    def save_results(self):
        """Save results to a text file"""
        if not self.full_output_data:
            self.show_message('warning', self.t['warn_title'], "No results to save")
            return

        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.full_output_data)
                self.show_message('success', "Success", f"Results saved to:\n{filename}")
            except Exception as e:
                self.show_message('error', self.t['error_title'], f"Failed to save results:\n{str(e)}")

    def tracking_error(self, error_msg):
        self.run_button.config(state="normal")
        self.status_label.config(
            text=self.t['status_error'],
            foreground="white",
            background=ViscumTheme.ERROR
        )
        self.progress_var.set(0)

        # More detailed error message
        error_detail = f"An error occurred during tracking:\n\n{error_msg}\n\nPlease check:\n"
        error_detail += "- Video file is valid and accessible\n"
        error_detail += "- All input values are correct\n"
        error_detail += "- ROI is within video bounds\n"
        error_detail += "- Frame range is valid"

        self.show_message('error', self.t['error_title'], error_detail)


def main():
    root = tk.Tk()
    app = ViscumGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
