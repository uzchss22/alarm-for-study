import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import time
import pygame

class StudyBreakTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("")

        # Set default values
        self.study_minutes = tk.IntVar(value=1)
        self.break_minutes = tk.IntVar(value=1)
        self.alarm_file = tk.StringVar()

        # Initialize pygame mixer
        pygame.mixer.init()

        # Study time setup
        tk.Label(root, text="Study Time (minutes):").grid(row=0, column=0, columnspan=2)
        self.study_spinbox = tk.Spinbox(root, from_=1, to_=120, increment=5, textvariable=self.study_minutes)
        self.study_spinbox.grid(row=1, column=0, columnspan=2)

        # Break time setup
        tk.Label(root, text="Break Time (minutes):").grid(row=2, column=0, columnspan=2)
        self.break_spinbox = tk.Spinbox(root, from_=1, to_=60, increment=5, textvariable=self.break_minutes)
        self.break_spinbox.grid(row=3, column=0, columnspan=2)

        # Alarm file setup
        tk.Label(root, text="Sound file path:").grid(row=4, column=0, columnspan=2)
        tk.Entry(root, textvariable=self.alarm_file).grid(row=5, column=0, columnspan=2)

        # Load image for browse button
        self.browse_image = tk.PhotoImage(file="folder20.png")
        tk.Button(root, image=self.browse_image, command=self.browse_file).grid(row=5, column=2)

        # Start button
        self.start_button = tk.Button(root, text="Start Timer", command=self.start_timer)
        self.start_button.grid(row=6, column=0)

        # Stop timer button
        self.stop_timer_button = tk.Button(root, text="Stop Timer", command=self.stop_timer)
        self.stop_timer_button.grid(row=6, column=1)

        # Stop sound button
        self.stop_sound_button = tk.Button(root, text="Stop Sound", command=self.stop_sound)
        self.stop_sound_button.grid(row=7, column=0, columnspan=2)

        # Protocol to handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Flag to control the timer
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
        self.start_button.config(state=tk.DISABLED)  # Disable start button to prevent multiple threads
        Thread(target=self.run_timer).start()

    def stop_timer(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)  # Enable start button when timer is stopped

    def stop_sound(self):
        pygame.mixer.music.stop()

    def run_timer(self):
        study_seconds = self.study_minutes.get() * 60
        break_seconds = self.break_minutes.get() * 60
        alarm_file = self.alarm_file.get()

        while self.running:
            # Study period
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

            # Break period
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
