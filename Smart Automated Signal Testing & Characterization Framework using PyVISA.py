# smart_signal_test_framework.py

"""
Smart Automated Signal Testing & Characterization Framework using PyVISA
Developed by [Your Name], Internship at Moog Bangalore
For Keysight 33500 Series Waveform Generator
"""

import pyvisa
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import time

# ====== CONFIGURABLE PARAMETERS ======
waveform_types = ["SIN", "SQU", "TRI"]     # Types of waveforms to test
start_freq = 1000       # Hz
stop_freq = 5000        # Hz
step_freq = 1000        # Hz
amplitudes = [1, 2, 3]  # Vpp values to test
delay_time = 1          # Seconds to wait between commands
log_file = "smart_signal_log.csv"

# ====== INSTRUMENT CONNECTION ======
print("Connecting to instrument...")
rm = pyvisa.ResourceManager()
devices = rm.list_resources()

if not devices:
    print("No VISA instruments found.")
    exit()

inst = rm.open_resource(devices[0])
idn = inst.query("*IDN?")
print("Connected to:", idn)

# ====== CSV LOGGING SETUP ======
with open(log_file, mode="a", newline='') as file:
    writer = csv.writer(file)
    file.seek(0, 2)
    if file.tell() == 0:
        writer.writerow(["Timestamp", "Waveform", "Frequency (Hz)", "Amplitude (Vpp)", "Measured Voltage (V)"])

# ====== SMART TEST ROUTINE ======
for waveform in waveform_types:
    for freq in range(start_freq, stop_freq + step_freq, step_freq):
        for amp in amplitudes:
            print(f"\nSetting {waveform} | Freq: {freq} Hz | Amp: {amp} Vpp")

            inst.write(f"FUNC {waveform}")
            inst.write(f"FREQ {freq}")
            inst.write(f"VOLT {amp}")
            time.sleep(delay_time)

            try:
                voltage = inst.query("MEAS:VOLT:DC?").strip()
                print(f"Measured Voltage: {voltage} V")
            except:
                voltage = "N/A"
                print("Voltage read not supported.")

            # Log data
            with open(log_file, mode="a", newline='') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.now(), waveform, freq, amp, voltage])

# ====== PLOT FINAL WAVEFORM SIMULATION ======
print("\nTest complete. Showing simulated plot for final setting...")
t = np.linspace(0, 1e-2, 1000)
final_f = freq
final_a = amp / 2
y = final_a * np.sin(2 * np.pi * final_f * t)

plt.plot(t, y)
plt.title(f"Simulated {waveform} Wave at {final_f} Hz")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (V)")
plt.grid(True)
plt.show()
