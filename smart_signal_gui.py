"""
Smart Automated Signal Testing & Characterization Framework with Tkinter GUI
Developed by [Your Name], Internship at Moog Bangalore
For Keysight 33500 Series Waveform Generator
"""

import pyvisa
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ====== CONFIGURABLE PARAMETERS ======
waveform_types = ["SIN", "SQU", "TRI"]
freq_min = 10      # Minimum frequency limit for validation (Hz)
freq_max = 1000000 # Max frequency limit for validation (Hz)
amp_min = 0.1      # Minimum amplitude limit (Vpp)
amp_max = 10       # Maximum amplitude limit (Vpp)
log_file = "smart_signal_log.csv"
delay_time = 1     # Seconds delay after settings

# ====== VISA INSTRUMENT CONNECTION ======
rm = pyvisa.ResourceManager()
devices = rm.list_resources()
if not devices:
    raise RuntimeError("No VISA instruments found. Connect the instrument and try again.")
inst = rm.open_resource(devices[0])
idn = inst.query("*IDN?").strip()

# ====== LOGGING SETUP ======
def init_log():
    try:
        with open(log_file, mode="r") as f:
            pass
    except FileNotFoundError:
        with open(log_file, mode="w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Waveform", "Frequency (Hz)", "Amplitude (Vpp)", "Measured Voltage (V)"])

init_log()

# ====== FUNCTION TO RUN TEST AND LOG ======
def run_test(waveform, freq, amp):
    try:
        inst.write(f"FUNC {waveform}")
        inst.write(f"FREQ {freq}")
        inst.write(f"VOLT {amp}")
        time.sleep(delay_time)
        voltage = inst.query("MEAS:VOLT:DC?").strip()
    except Exception:
        voltage = "N/A"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, mode="a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, waveform, freq, amp, voltage])

    return voltage

# ====== GUI APP ======
class SignalTestApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Signal Test Framework - Moog Internship")
        self.geometry("450x350")
        self.resizable(False, False)

        # Instrument ID label
        ttk.Label(self, text=f"Connected Instrument: {idn}", foreground="blue").pack(pady=5)

        # Waveform selector
        ttk.Label(self, text="Select Waveform:").pack()
        self.waveform_var = tk.StringVar(value=waveform_types[0])
        self.waveform_combo = ttk.Combobox(self, textvariable=self.waveform_var, values=waveform_types, state="readonly")
        self.waveform_combo.pack(pady=5)

        # Frequency entry
        ttk.Label(self, text=f"Frequency (Hz) [{freq_min} - {freq_max}]:").pack()
        self.freq_var = tk.IntVar(value=1000)
        self.freq_entry = ttk.Entry(self, textvariable=self.freq_var)
        self.freq_entry.pack(pady=5)

        # Amplitude entry
        ttk.Label(self, text=f"Amplitude (Vpp) [{amp_min} - {amp_max}]:").pack()
        self.amp_var = tk.DoubleVar(value=1.0)
        self.amp_entry = ttk.Entry(self, textvariable=self.amp_var)
        self.amp_entry.pack(pady=5)

        # Start test button
        self.start_button = ttk.Button(self, text="Start Test", command=self.start_test)
        self.start_button.pack(pady=10)

        # Output label
        self.output_label = ttk.Label(self, text="", foreground="green")
        self.output_label.pack(pady=5)

        # Plot button
        self.plot_button = ttk.Button(self, text="Show Simulated Waveform Plot", command=self.plot_waveform)
        self.plot_button.pack(pady=10)

        # To store last test parameters for plotting
        self.last_waveform = waveform_types[0]
        self.last_freq = 1000
        self.last_amp = 1.0

    def validate_inputs(self):
        try:
            freq = self.freq_var.get()
            amp = self.amp_var.get()
        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
            return False

        if freq < freq_min or freq > freq_max:
            messagebox.showerror("Frequency Out of Range", f"Frequency must be between {freq_min} Hz and {freq_max} Hz.")
            return False
        if amp < amp_min or amp > amp_max:
            messagebox.showerror("Amplitude Out of Range", f"Amplitude must be between {amp_min} Vpp and {amp_max} Vpp.")
            return False
        return True

    def start_test(self):
        if not self.validate_inputs():
            return
        self.start_button.config(state="disabled")
        waveform = self.waveform_var.get()
        freq = self.freq_var.get()
        amp = self.amp_var.get()

        def test_thread():
            voltage = run_test(waveform, freq, amp)
            self.last_waveform = waveform
            self.last_freq = freq
            self.last_amp = amp
            self.output_label.config(text=f"Test Complete: Measured Voltage = {voltage} V")
            self.start_button.config(state="normal")

        threading.Thread(target=test_thread).start()

    def plot_waveform(self):
        t = np.linspace(0, 1e-3, 1000)  # 1 ms duration
        f = self.last_freq
        a = self.last_amp / 2  # peak amplitude
        waveform = self.last_waveform

        if waveform == "SIN":
            y = a * np.sin(2 * np.pi * f * t)
        elif waveform == "SQU":
            y = a * np.sign(np.sin(2 * np.pi * f * t))
        elif waveform == "TRI":
            y = a * (2 / np.pi) * np.arcsin(np.sin(2 * np.pi * f * t))
        else:
            y = np.zeros_like(t)

        plt.figure(figsize=(8,4))
        plt.plot(t * 1000, y)  # time in ms
        plt.title(f"Simulated {waveform} Waveform at {f} Hz")
        plt.xlabel("Time (ms)")
        plt.ylabel("Amplitude (V)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = SignalTestApp()
    app.mainloop()
