import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import time
import pygame
import os
import sys

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for development and for PyInstaller bundled exe. """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class StudyBreakTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_alarm_file = resource_path("default_sound.mp3")

        self.study_minutes = tk.IntVar(value=25)
        self.break_minutes = tk.IntVar(value=10)
        self.alarm_file = tk.StringVar(value=default_alarm_file)

        pygame.mixer.init()

        for i in range(4):
            root.grid_columnconfigure(i, weight=1)

        tk.Label(root, text="Study Time (minutes):").grid(row=0, column=0, columnspan=4, sticky="ew")
        self.study_spinbox = tk.Spinbox(root, from_=5, to_=120, increment=5, textvariable=self.study_minutes)
        self.study_spinbox.grid(row=1, column=0, columnspan=4, sticky="ew")

        tk.Label(root, text="Break Time (minutes):").grid(row=2, column=0, columnspan=4, sticky="ew")
        self.break_spinbox = tk.Spinbox(root, from_=5, to_=60, increment=5, textvariable=self.break_minutes)
        self.break_spinbox.grid(row=3, column=0, columnspan=4, sticky="ew")

        tk.Label(root, text="Sound file path:").grid(row=4, column=0, columnspan=4, sticky="ew")
        tk.Entry(root, textvariable=self.alarm_file).grid(row=5, column=0, columnspan=3, sticky="ew")

        self.browse_image = tk.PhotoImage(file=resource_path("folder.png"))
        self.play_image = tk.PhotoImage(file=resource_path("play.png"))
        self.stop_image = tk.PhotoImage(file=resource_path("stop.png"))
        self.mute_image = tk.PhotoImage(file=resource_path("mute.png"))

        browse_button = tk.Button(root, image=self.browse_image, command=self.browse_file)
        browse_button.grid(row=5, column=3, sticky="ew")
        ToolTip(browse_button, "Browse for an alarm sound file")

        
        self.start_button = tk.Button(root, image=self.play_image, command=self.start_timer)
        self.start_button.grid(row=6, column=0, columnspan=2, sticky="ew")
        ToolTip(self.start_button, "Start the study timer")

        
        self.stop_timer_button = tk.Button(root, image=self.stop_image, command=self.stop_timer)
        self.stop_timer_button.grid(row=6, column=2, columnspan=2, sticky="ew")
        ToolTip(self.stop_timer_button, "Stop the study timer")

        
        self.stop_sound_button = tk.Button(root, image=self.mute_image, command=self.stop_sound)
        self.stop_sound_button.grid(row=7, column=0, columnspan=4, sticky="ew")
        ToolTip(self.stop_sound_button, "Stop the alarm sound")

        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        
        self.running = False

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if file_path:
            self.alarm_file.set(file_path)

    def start_timer(self):
        if not self.alarm_file.get():
            messagebox.showwarning("Warning", "Please select an alarm sound file.")
            return
        self.running = True
        self.start_button.config(state=tk.DISABLED)  
        Thread(target=self.run_timer).start()

    def stop_timer(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)  

    def stop_sound(self):
        pygame.mixer.music.stop()

    def run_timer(self):
        study_seconds = self.study_minutes.get() * 60
        break_seconds = self.break_minutes.get() * 60
        alarm_file = self.alarm_file.get()

        while self.running:
            for _ in range(study_seconds):
                if not self.running:
                    return
                time.sleep(1)
            pygame.mixer.music.load(alarm_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy() and self.running:
                time.sleep(1)

            if not self.running:
                return

            for _ in range(break_seconds):
                if not self.running:
                    return
                time.sleep(1)
            pygame.mixer.music.load(alarm_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy() and self.running:
                time.sleep(1)

    def on_closing(self):
        self.stop_timer()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyBreakTimer(root)
    root.mainloop()
