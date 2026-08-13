"""
Speed Tester GUI - Tkinter-based Interactive Speed Testing Tool
Allows visual speed testing with calibration, measurement, and analysis
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import numpy as np
from opencv_speed_detection import (
    OpenCVSpeedDetector, CalibrationTool, VideoAnalyzer, ExportManager
)
from typing import Optional, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class SpeedTesterGUI:
    """Main GUI application for speed testing"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚗 OpenCV Speed Tester")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1a1a1a")
        
        # Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Dark.TFrame', background='#1a1a1a')
        self.style.configure('Dark.TLabel', background='#1a1a1a', foreground='#ffffff')
        self.style.configure('Dark.TButton', background='#2a2a2a', foreground='#ffffff')
        
        # Core components
        self.detector = OpenCVSpeedDetector(pixels_per_meter=20.0, fps=30.0)
        self.calibrator = CalibrationTool()
        self.cap: Optional[cv2.VideoCapture] = None
        self.current_video_path = ""
        
        # State
        self.playing = False
        self.calibration_mode = False
        self.running = False
        self.frame_number = 0
        self.total_frames = 0
        
        # Video dimensions
        self.video_width = 640
        self.video_height = 480
        
        # Build UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control Panel
        self.setup_control_panel(main_frame)
        
        # Video Display
        self.setup_video_display(main_frame)
        
        # Statistics
        self.setup_statistics_panel(main_frame)
        
    def setup_control_panel(self, parent):
        """Setup control panel"""
        control_frame = ttk.LabelFrame(parent, text="📋 Controls", style='Dark.TFrame')
        control_frame.pack(fill=tk.X, pady=10)
        
        # Top row - File operations
        file_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(file_frame, text="📁 Load Video", 
                  command=self.load_video).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="📷 Load Camera", 
                  command=self.load_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="🎬 Play/Pause", 
                  command=self.toggle_play).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="🔄 Reset", 
                  command=self.reset).pack(side=tk.LEFT, padx=5)
        
        # Second row - Calibration
        calib_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        calib_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(calib_frame, text="⚙️ Calibration Mode", 
                  command=self.enter_calibration_mode).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(calib_frame, text="Pixels/Meter:", style='Dark.TLabel').pack(side=tk.LEFT, padx=5)
        self.ppm_spinbox = ttk.Spinbox(calib_frame, from_=1, to=100, width=10)
        self.ppm_spinbox.set(20)
        self.ppm_spinbox.pack(side=tk.LEFT, padx=5)
        self.ppm_spinbox.bind('<KeyRelease>', lambda e: self.update_ppm())
        
        # Third row - Measurement
        measure_frame = ttk.Frame(control_frame, style='Dark.TFrame')
        measure_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(measure_frame, text="📏 Measure Speed", 
                  command=self.manual_speed_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(measure_frame, text="📊 Show Graph", 
                  command=self.show_speed_graph).pack(side=tk.LEFT, padx=5)
        ttk.Button(measure_frame, text="💾 Export Results", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Info display
        self.info_label = ttk.Label(control_frame, 
                                    text="Ready. Load a video or camera to start.",
                                    style='Dark.TLabel')
        self.info_label.pack(fill=tk.X, padx=10, pady=10)
        
    def setup_video_display(self, parent):
        """Setup video display area"""
        video_frame = ttk.LabelFrame(parent, text="🎥 Video Display", style='Dark.TFrame')
        video_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Canvas for video
        self.canvas = tk.Canvas(video_frame, bg='#000000',
                               width=self.video_width, height=self.video_height)
        self.canvas.pack(padx=10, pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(video_frame, 
                                     from_=0, to=100,
                                     orient=tk.HORIZONTAL,
                                     variable=self.progress_var,
                                     command=self.seek_video)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Frame counter
        self.frame_label = ttk.Label(video_frame,
                                    text="Frame: 0/0",
                                    style='Dark.TLabel')
        self.frame_label.pack(fill=tk.X, padx=10, pady=5)
        
    def setup_statistics_panel(self, parent):
        """Setup statistics panel"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Statistics", style='Dark.TFrame')
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Create grid for stats
        stats_grid = ttk.Frame(stats_frame, style='Dark.TFrame')
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Statistics labels
        self.stats_labels = {}
        stats_list = [
            'vehicles', 'avg_speed', 'max_speed', 'min_speed', 
            'measurements', 'ppm'
        ]
        
        for i, stat in enumerate(stats_list):
            row = i // 3
            col = i % 3
            
            label_text = {
                'vehicles': '🚗 Vehicles',
                'avg_speed': '📊 Avg Speed',
                'max_speed': '⬆️ Max Speed',
                'min_speed': '⬇️ Min Speed',
                'measurements': '📈 Measurements',
                'ppm': '⚙️ PPM'
            }
            
            frame = ttk.Frame(stats_grid, style='Dark.TFrame')
            frame.grid(row=row, column=col, padx=10, pady=5, sticky='ew')
            
            ttk.Label(frame, text=label_text[stat] + ":",
                     style='Dark.TLabel').pack(side=tk.LEFT)
            
            value_label = ttk.Label(frame, text="0",
                                   style='Dark.TLabel', foreground='#00ff00')
            value_label.pack(side=tk.LEFT, padx=10)
            
            self.stats_labels[stat] = value_label
        
        # Update stats display
        self.update_statistics()
        
    def load_video(self):
        """Load video file"""
        filepath = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        self.current_video_path = filepath
        self.cap = cv2.VideoCapture(filepath)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open video file")
            return
        
        # Get video info
        info = VideoAnalyzer.get_video_info(filepath)
        self.video_width = info['width']
        self.video_height = info['height']
        self.total_frames = info['frame_count']
        self.detector.fps = info['fps']
        
        self.info_label.config(
            text=f"✓ Loaded: {filepath.split('/')[-1]} | "
                 f"{info['width']}x{info['height']} | "
                 f"{info['fps']:.0f} FPS | {info['duration_seconds']}s"
        )
        
        self.playing = True
        self.frame_number = 0
        self.process_video()
        
    def load_camera(self):
        """Load camera"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera")
            return
        
        self.info_label.config(text="✓ Camera opened")
        self.playing = True
        self.process_video()
        
    def process_video(self):
        """Process video frames"""
        if not self.cap or not self.playing:
            return
        
        ret, frame = self.cap.read()
        
        if not ret:
            if self.current_video_path:  # Video file ended
                self.playing = False
                self.update_statistics()
                return
            else:  # Camera - restart
                self.frame_number = 0
        else:
            self.frame_number += 1
            self.progress_var.set(
                (self.frame_number / max(self.total_frames, 1)) * 100
            )
            
            # Resize frame for display
            display_frame = cv2.resize(frame, (self.video_width, self.video_height))
            
            # Apply calibration overlay if in calibration mode
            if self.calibration_mode:
                display_frame = self.calibrator.draw_calibration_line(
                    display_frame, 3.0  # 3 meter reference
                )
            
            # Display frame
            self.display_frame(display_frame)
            
            # Update frame counter
            self.frame_label.config(
                text=f"Frame: {self.frame_number}/{self.total_frames}"
            )
        
        # Continue processing
        self.root.after(int(1000 / self.detector.fps), self.process_video)
        
    def display_frame(self, frame):
        """Display frame on canvas"""
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PhotoImage
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image)
        
        # Update canvas
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.canvas.image = photo
        
    def toggle_play(self):
        """Toggle play/pause"""
        if self.cap:
            self.playing = not self.playing
            if self.playing:
                self.info_label.config(text="▶️ Playing...")
                self.process_video()
            else:
                self.info_label.config(text="⏸️ Paused")
        
    def reset(self):
        """Reset everything"""
        self.playing = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.detector.reset_all()
        self.calibrator = CalibrationTool()
        self.frame_number = 0
        self.total_frames = 0
        self.info_label.config(text="Reset. Load a video or camera to start.")
        self.canvas.create_rectangle(0, 0, self.video_width, self.video_height,
                                    fill='black')
        self.update_statistics()
        
    def enter_calibration_mode(self):
        """Enter calibration mode"""
        self.calibration_mode = not self.calibration_mode
        if self.calibration_mode:
            self.info_label.config(text="📏 Calibration Mode: Draw a line for known distance")
        else:
            self.info_label.config(text="Calibration Mode Off")
        
    def update_ppm(self):
        """Update pixels per meter"""
        try:
            ppm = float(self.ppm_spinbox.get())
            self.detector.pixels_per_meter = ppm
            self.info_label.config(text=f"⚙️ Pixels/Meter updated to {ppm}")
        except ValueError:
            pass
        
    def manual_speed_input(self):
        """Manual speed input dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Measure Speed")
        dialog.geometry("400x300")
        dialog.configure(bg="#1a1a1a")
        
        ttk.Label(dialog, text="Vehicle ID:", style='Dark.TLabel').pack(pady=5)
        vehicle_id_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=vehicle_id_var, width=20).pack(pady=5)
        
        ttk.Label(dialog, text="Speed (km/h):", style='Dark.TLabel').pack(pady=5)
        speed_var = tk.StringVar(value="60")
        ttk.Entry(dialog, textvariable=speed_var, width=20).pack(pady=5)
        
        def record_measurement():
            try:
                vehicle_id = int(vehicle_id_var.get())
                speed_kmh = float(speed_var.get())
                speed_mph = speed_kmh / 1.609
                
                # Store in detector
                if vehicle_id not in self.detector.speed_history:
                    self.detector.speed_history[vehicle_id] = []
                self.detector.speed_history[vehicle_id].append(speed_kmh)
                
                self.info_label.config(
                    text=f"✓ Recorded: Vehicle {vehicle_id} @ {speed_kmh:.1f} km/h"
                )
                self.update_statistics()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid input")
        
        ttk.Button(dialog, text="Record", command=record_measurement).pack(pady=20)
        
    def show_speed_graph(self):
        """Show speed graph"""
        if not self.detector.speed_history:
            messagebox.showinfo("No Data", "No speed measurements yet")
            return
        
        # Create figure
        fig = Figure(figsize=(10, 6), dpi=100, facecolor='#1a1a1a')
        ax = fig.add_subplot(111, facecolor='#2a2a2a')
        
        # Plot speed data
        for vehicle_id, speeds in self.detector.speed_history.items():
            ax.plot(speeds, label=f"Vehicle {vehicle_id}", marker='o')
        
        ax.set_xlabel("Frame", color='white')
        ax.set_ylabel("Speed (km/h)", color='white')
        ax.set_title("Vehicle Speed Analysis", color='white')
        ax.legend(facecolor='#2a2a2a', edgecolor='white')
        ax.tick_params(colors='white')
        
        # Create window
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Speed Graph")
        graph_window.geometry("800x600")
        graph_window.configure(bg="#1a1a1a")
        
        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def export_results(self):
        """Export results to file"""
        if not self.detector.measurements:
            messagebox.showinfo("No Data", "No measurements to export")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("Text", "*.txt")]
        )
        
        if not filepath:
            return
        
        format_type = filepath.split('.')[-1].lower()
        if ExportManager.export_measurements(
            self.detector.measurements, filepath, format_type
        ):
            messagebox.showinfo("Success", f"Results exported to {filepath}")
            self.info_label.config(text=f"✓ Exported to {filepath}")
        else:
            messagebox.showerror("Error", "Export failed")
            
    def seek_video(self, value):
        """Seek video to position"""
        if self.cap and self.total_frames > 0:
            frame_pos = int((float(value) / 100) * self.total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            self.frame_number = frame_pos
            
    def update_statistics(self):
        """Update statistics display"""
        stats = self.detector.get_statistics()
        
        self.stats_labels['vehicles'].config(text=str(stats['total_vehicles']))
        self.stats_labels['avg_speed'].config(text=f"{stats['avg_speed_kmh']:.1f}")
        self.stats_labels['max_speed'].config(text=f"{stats['max_speed_kmh']:.1f}")
        self.stats_labels['min_speed'].config(text=f"{stats['min_speed_kmh']:.1f}")
        self.stats_labels['measurements'].config(text=str(stats['measurements']))
        self.stats_labels['ppm'].config(text=f"{stats['pixels_per_meter']:.1f}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SpeedTesterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
