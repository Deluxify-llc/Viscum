#!/usr/bin/env python3
# GUI for Viscum ball tracker

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import threading
import os

class ViscumGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Viscum - Ball Tracker")
        self.root.geometry("1200x800")

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

        self.setup_ui()

    def setup_ui(self):
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_panel = ttk.Frame(main_container, width=350)
        main_container.add(left_panel, weight=0)

        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)

        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)

    def setup_left_panel(self, parent):
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
        video_frame = ttk.LabelFrame(scrollable_frame, text="1. Video Selection", padding=10)
        video_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(video_frame, text="Browse Video", command=self.browse_video).pack(fill=tk.X, pady=2)
        ttk.Label(video_frame, textvariable=self.video_path, wraplength=300, foreground="blue").pack(fill=tk.X, pady=2)

        self.video_info_label = ttk.Label(video_frame, text="No video loaded", foreground="gray")
        self.video_info_label.pack(fill=tk.X, pady=2)

        # ROI selection
        roi_frame = ttk.LabelFrame(scrollable_frame, text="2. ROI Selection", padding=10)
        roi_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(roi_frame, text="Select ROI on Video", command=self.select_roi_interactive).pack(fill=tk.X, pady=2)

        roi_grid = ttk.Frame(roi_frame)
        roi_grid.pack(fill=tk.X, pady=5)

        ttk.Label(roi_grid, text="X1:").grid(row=0, column=0, sticky=tk.W, padx=2)
        ttk.Entry(roi_grid, textvariable=self.roi_x1, width=8).grid(row=0, column=1, padx=2)
        ttk.Label(roi_grid, text="Y1:").grid(row=0, column=2, sticky=tk.W, padx=2)
        ttk.Entry(roi_grid, textvariable=self.roi_y1, width=8).grid(row=0, column=3, padx=2)

        ttk.Label(roi_grid, text="X2:").grid(row=1, column=0, sticky=tk.W, padx=2)
        ttk.Entry(roi_grid, textvariable=self.roi_x2, width=8).grid(row=1, column=1, padx=2)
        ttk.Label(roi_grid, text="Y2:").grid(row=1, column=2, sticky=tk.W, padx=2)
        ttk.Entry(roi_grid, textvariable=self.roi_y2, width=8).grid(row=1, column=3, padx=2)

        # Frame Range
        frame_frame = ttk.LabelFrame(scrollable_frame, text="3. Frame Range", padding=10)
        frame_frame.pack(fill=tk.X, padx=5, pady=5)

        frame_grid = ttk.Frame(frame_frame)
        frame_grid.pack(fill=tk.X)

        ttk.Label(frame_grid, text="Start Frame:").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(frame_grid, textvariable=self.start_frame, width=10).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(frame_grid, text="End Frame:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(frame_grid, textvariable=self.end_frame, width=10).grid(row=1, column=1, padx=2, pady=2)

        ttk.Button(frame_frame, text="Preview Frame", command=self.preview_frame).pack(fill=tk.X, pady=5)

        # Ball Properties
        ball_frame = ttk.LabelFrame(scrollable_frame, text="4. Ball Properties", padding=10)
        ball_frame.pack(fill=tk.X, padx=5, pady=5)

        ball_grid = ttk.Frame(ball_frame)
        ball_grid.pack(fill=tk.X)

        ttk.Label(ball_grid, text="Diameter (mm):").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(ball_grid, textvariable=self.ball_diameter_mm, width=10).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(ball_grid, text="Density (kg/m³):").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(ball_grid, textvariable=self.ball_density, width=10).grid(row=1, column=1, padx=2, pady=2)

        # Liquid Properties
        liquid_frame = ttk.LabelFrame(scrollable_frame, text="5. Liquid Properties", padding=10)
        liquid_frame.pack(fill=tk.X, padx=5, pady=5)

        liquid_grid = ttk.Frame(liquid_frame)
        liquid_grid.pack(fill=tk.X)

        ttk.Label(liquid_grid, text="Density (kg/m³):").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(liquid_grid, textvariable=self.liquid_density, width=10).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(liquid_grid, text="Gravity (m/s²):").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        ttk.Entry(liquid_grid, textvariable=self.gravity, width=10).grid(row=1, column=1, padx=2, pady=2)

        # calibration test option
        calib_frame = ttk.LabelFrame(scrollable_frame, text="6. Calibration (Optional)", padding=10)
        calib_frame.pack(fill=tk.X, padx=5, pady=5)

        self.is_calibration = tk.BooleanVar(value=False)
        ttk.Checkbutton(calib_frame, text="This is a calibration test",
                       variable=self.is_calibration,
                       command=self.toggle_calibration).pack(anchor=tk.W, pady=2)

        self.calib_inputs = ttk.Frame(calib_frame)

        ttk.Label(self.calib_inputs, text="Temperature (°C):").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.temp = tk.DoubleVar(value=25.0)
        ttk.Entry(self.calib_inputs, textvariable=self.temp, width=10).grid(row=0, column=1, padx=2, pady=2)

        ttk.Label(self.calib_inputs, text="Viscosity @ 40°C (cP):").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.visc_40 = tk.DoubleVar(value=0.0)
        ttk.Entry(self.calib_inputs, textvariable=self.visc_40, width=10).grid(row=1, column=1, padx=2, pady=2)

        ttk.Label(self.calib_inputs, text="Viscosity @ 100°C (cP):").grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.visc_100 = tk.DoubleVar(value=0.0)
        ttk.Entry(self.calib_inputs, textvariable=self.visc_100, width=10).grid(row=2, column=1, padx=2, pady=2)

        # run button
        run_frame = ttk.Frame(scrollable_frame, padding=10)
        run_frame.pack(fill=tk.X, padx=5, pady=10)

        self.run_button = ttk.Button(run_frame, text="Run Tracking", command=self.run_tracking)
        self.run_button.pack(fill=tk.X, pady=2)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(run_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(run_frame, text="Ready", foreground="green")
        self.status_label.pack(fill=tk.X)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def toggle_calibration(self):
        if self.is_calibration.get():
            self.calib_inputs.pack(fill=tk.X, pady=5)
        else:
            self.calib_inputs.pack_forget()

    def setup_right_panel(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(preview_frame, bg="black", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # frame controls
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(nav_frame, text="◀◀", command=lambda: self.navigate_frame(-10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="◀", command=lambda: self.navigate_frame(-1)).pack(side=tk.LEFT, padx=2)

        self.frame_scale = ttk.Scale(nav_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=self.on_frame_scale)
        self.frame_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        ttk.Button(nav_frame, text="▶", command=lambda: self.navigate_frame(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="▶▶", command=lambda: self.navigate_frame(10)).pack(side=tk.LEFT, padx=2)

        self.frame_label = ttk.Label(nav_frame, text="Frame: 0/0")
        self.frame_label.pack(side=tk.LEFT, padx=10)

    def browse_video(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )

        if filename:
            self.video_path.set(filename)
            self.load_video(filename)

    def load_video(self, path):
        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(path)

        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open video file")
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.video_info_label.config(
            text=f"FPS: {self.fps:.1f} | Frames: {self.total_frames}",
            foreground="green"
        )

        self.frame_scale.config(to=self.total_frames - 1)
        self.end_frame.set(min(self.total_frames - 1, self.end_frame.get()))

        # Load first frame
        self.show_frame(0)

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

            # Resize to fit canvas
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

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # Keep reference

            self.frame_label.config(text=f"Frame: {frame_num}/{self.total_frames-1}")
            self.frame_scale.set(frame_num)
        finally:
            self.updating_frame = False

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
            messagebox.showwarning("Warning", "Please load a video first")
            return
        self.show_frame(self.start_frame.get())

    def select_roi_interactive(self):
        if not self.cap:
            messagebox.showwarning("Warning", "Please load a video first")
            return

        self.selecting_roi = True
        self.status_label.config(text="Click and drag to select ROI", foreground="blue")

    def on_canvas_click(self, event):
        if self.selecting_roi and self.current_frame is not None and self.display_scale > 0:
            # Convert canvas coordinates to image coordinates
            x = int(event.x / self.display_scale)
            y = int(event.y / self.display_scale)
            self.roi_start = (x, y)

    def on_canvas_drag(self, event):
        if self.selecting_roi and self.roi_start and self.display_scale > 0:
            x = int(event.x / self.display_scale)
            y = int(event.y / self.display_scale)

            self.roi_x1.set(min(self.roi_start[0], x))
            self.roi_y1.set(min(self.roi_start[1], y))
            self.roi_x2.set(max(self.roi_start[0], x))
            self.roi_y2.set(max(self.roi_start[1], y))

            self.show_frame(self.current_frame_num)

    def on_canvas_release(self, event):
        if self.selecting_roi:
            self.selecting_roi = False
            self.roi_start = None
            self.status_label.config(text="ROI selected", foreground="green")

    def run_tracking(self):
        if not self.video_path.get():
            messagebox.showwarning("Warning", "Please select a video file")
            return

        # Run in separate thread
        thread = threading.Thread(target=self.execute_tracking)
        thread.daemon = True
        thread.start()

    def execute_tracking(self):
        self.run_button.config(state="disabled")
        self.status_label.config(text="Running tracking...", foreground="orange")

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
                f'{sys.executable} VideoProcessor.py < {params_file}',
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
        self.status_label.config(text="Tracking complete!", foreground="green")
        self.progress_var.set(100)

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

        # Show results window
        self.show_results_window(results, output)

    def show_results_window(self, results, full_output):
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("Tracking Results")
        results_window.geometry("600x500")

        # Main frame
        main_frame = ttk.Frame(results_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title = ttk.Label(main_frame, text="Viscosity Measurement Results",
                         font=('Arial', 14, 'bold'))
        title.pack(pady=(0, 15))

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Calculated Values", padding=15)
        results_frame.pack(fill=tk.X, pady=10)

        if results:
            row = 0
            if 'avg_diameter' in results:
                ttk.Label(results_frame, text="Average Ball Diameter:",
                         font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['avg_diameter']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'velocity' in results:
                ttk.Label(results_frame, text="Final Velocity (pixels/s):",
                         font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['velocity']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'mm_per_pixel' in results:
                ttk.Label(results_frame, text="Pixel to mm Conversion:",
                         font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['mm_per_pixel']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'mm_velocity' in results:
                ttk.Label(results_frame, text="Velocity (mm/s):",
                         font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
                ttk.Label(results_frame, text=results['mm_velocity']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=5)
                row += 1

            if 'viscosity' in results:
                ttk.Label(results_frame, text="").grid(row=row, column=0, pady=5)
                row += 1

                # Highlight viscosity result
                visc_frame = ttk.Frame(results_frame, relief=tk.RIDGE, borderwidth=2)
                visc_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)

                ttk.Label(visc_frame, text="MEASURED VISCOSITY:",
                         font=('Arial', 12, 'bold'), foreground='blue').pack(side=tk.LEFT, padx=10, pady=10)
                ttk.Label(visc_frame, text=results['viscosity'],
                         font=('Arial', 12, 'bold'), foreground='green').pack(side=tk.LEFT, padx=10, pady=10)
                row += 1

            # Calibration results if present
            if 'calculated_viscosity' in results:
                ttk.Label(results_frame, text="").grid(row=row, column=0, pady=5)
                row += 1

                # Calibration section
                calib_label = ttk.Label(results_frame, text="Calibration Results",
                                       font=('Arial', 11, 'bold', 'underline'))
                calib_label.grid(row=row, column=0, columnspan=2, pady=5)
                row += 1

                if 'activation_energy' in results:
                    ttk.Label(results_frame, text="Activation Energy:",
                             font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=3)
                    ttk.Label(results_frame, text=results['activation_energy']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
                    row += 1

                if 'pre_exp_factor' in results:
                    ttk.Label(results_frame, text="Pre-exponential Factor:",
                             font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=3)
                    ttk.Label(results_frame, text=results['pre_exp_factor']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
                    row += 1

                ttk.Label(results_frame, text="Expected Viscosity:",
                         font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=3)
                ttk.Label(results_frame, text=results['calculated_viscosity']).grid(row=row, column=1, sticky=tk.W, padx=10, pady=3)
                row += 1

                if 'error' in results:
                    error_val = results['error']

                    # Determine color based on error value
                    try:
                        error_num = float(error_val)
                        color = 'red' if error_num > 0.1 else 'green'
                        # Convert to percentage for display
                        error_percent = f"{error_num * 100:.2f}%"
                    except:
                        color = 'orange'
                        error_percent = error_val

                    # Highlight error result in a frame
                    error_frame = ttk.Frame(results_frame, relief=tk.RIDGE, borderwidth=2)
                    error_frame.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)

                    ttk.Label(error_frame, text="RELATIVE ERROR:",
                             font=('Arial', 11, 'bold'), foreground='blue').pack(side=tk.LEFT, padx=10, pady=10)
                    ttk.Label(error_frame, text=error_percent,
                             font=('Arial', 11, 'bold'), foreground=color).pack(side=tk.LEFT, padx=10, pady=10)
                    row += 1

        else:
            ttk.Label(results_frame, text="Could not parse results. See full output below.").pack()

        # Full output
        output_frame = ttk.LabelFrame(main_frame, text="Full Output", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Text widget with scrollbar
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=10,
                             yscrollcommand=scrollbar.set, font=('Courier', 9))
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        text_widget.insert('1.0', full_output)
        text_widget.config(state=tk.DISABLED)

        # Close button
        ttk.Button(main_frame, text="Close", command=results_window.destroy).pack(pady=10)

    def tracking_error(self, error_msg):
        self.run_button.config(state="normal")
        self.status_label.config(text="Error occurred", foreground="red")
        self.progress_var.set(0)

        messagebox.showerror("Error", f"Tracking failed:\n{error_msg}")


def main():
    root = tk.Tk()
    app = ViscumGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
