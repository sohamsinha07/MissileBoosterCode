import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

def calculate():
    """ Perform real multi-stage rocket ΔV and Range calculations """
    g0 = 9.81  # gravity acceleration (m/s^2)

    # Read Inputs
    booster_size = float(entries["Booster Size (kg)"].get())
    mass_stage1 = float(entries["Mass Stage 1 (kg)"].get())
    mass_stage2 = float(entries["Mass Stage 2 (kg)"].get())
    mass_stage3 = float(entries["Mass Stage 3 (kg)"].get())
    diameter = float(entries["Diameter (m)"].get())
    length = float(entries["Length (m)"].get())
    isp = float(entries["ISP (s)"].get())

    ve = isp * g0

    propellant_fraction = 0.8  # Example 80% propellant

    # Mass setup
    payload_mass = booster_size
    mass3_initial = mass_stage3
    mass3_propellant = mass3_initial * propellant_fraction
    mass3_final = mass3_initial - mass3_propellant

    mass2_initial = mass_stage2 + mass3_final
    mass2_propellant = mass_stage2 * propellant_fraction
    mass2_final = mass2_initial - mass2_propellant

    mass1_initial = mass_stage1 + mass2_final
    mass1_propellant = mass_stage1 * propellant_fraction
    mass1_final = mass1_initial - mass1_propellant

    # Delta-V calculations
    delta_v_stage1 = ve * math.log(mass1_initial / mass1_final)
    delta_v_stage2 = ve * math.log(mass2_initial / mass2_final)
    delta_v_stage3 = ve * math.log(mass3_initial / mass3_final)

    delta_v_values = [delta_v_stage1, delta_v_stage2, delta_v_stage3]
    total_delta_v = sum(delta_v_values)

    estimated_range = total_delta_v * 0.5  # Simple estimate

    # Update Outputs
    for i in range(3):
        delta_v_labels[i].config(text=f"Stage {i+1} ΔV: {delta_v_values[i]:.2f} m/s")

    total_delta_v_label.config(text=f"Total ΔV: {total_delta_v:.2f} m/s")
    range_label.config(text=f"Estimated Range: {estimated_range:.2f} km")

    plot_graph(delta_v_values, total_delta_v)

def plot_graph(delta_v_values, total_delta_v):
    """ Plot the Delta-V distribution """
    ax.clear()
    stages = ["Stage 1", "Stage 2", "Stage 3", "Total"]
    values = delta_v_values + [total_delta_v]
    ax.bar(stages, values, color=["#004080", "#0059b3", "#0073e6", "#00008B"])
    ax.set_ylabel("ΔV (m/s)", fontsize=12, color="white")
    ax.set_title("Stage-wise ΔV and Total ΔV", fontsize=14, color="white")
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    fig.patch.set_facecolor('#0d1b2a')
    ax.set_facecolor('#0d1b2a')
    canvas.draw()

# ----------------- Navy Theme -----------------
bg_color = "#0d1b2a"    # Dark Navy
frame_color = "#1b263b" # Slightly lighter navy
font_color = "white"

root = tk.Tk()
root.title("Missile Booster Performance - United States Navy")
root.geometry("800x850")
root.configure(bg=bg_color)

# ----------------- Input Frame -----------------
input_frame = ttk.LabelFrame(root, text="Input Parameters", style="TLabelframe")
input_frame.pack(padx=20, pady=10, fill="both")

params = ["Booster Size (kg)", "Mass Stage 1 (kg)", "Mass Stage 2 (kg)", "Mass Stage 3 (kg)", "Diameter (m)", "Length (m)", "ISP (s)"]
entries = {}

for param in params:
    frame = ttk.Frame(input_frame)
    frame.pack(fill="x", padx=10, pady=5)
    label = ttk.Label(frame, text=param, foreground=font_color, background=frame_color, font=("Helvetica", 12))
    label.pack(side="left", padx=5)
    entry = ttk.Entry(frame, width=15, font=("Helvetica", 12))
    entry.pack(side="right", padx=5)
    entries[param] = entry

# ----------------- Calculate Button -----------------
calculate_button = tk.Button(root, text="CALCULATE PERFORMANCE", command=calculate,
                             bg="#00008B", fg="white", font=("Helvetica", 14, "bold"), relief="raised")
calculate_button.pack(pady=20)

# ----------------- Output Frame -----------------
output_frame = ttk.LabelFrame(root, text="Outputs", style="TLabelframe")
output_frame.pack(padx=20, pady=10, fill="both")

delta_v_labels = []
for i in range(3):
    lbl = tk.Label(output_frame, text=f"Stage {i+1} ΔV: ", fg=font_color, bg=frame_color, font=("Helvetica", 12))
    lbl.pack(pady=2)
    delta_v_labels.append(lbl)

total_delta_v_label = tk.Label(output_frame, text="Total ΔV: ", fg=font_color, bg=frame_color, font=("Helvetica", 12, "bold"))
total_delta_v_label.pack(pady=5)

range_label = tk.Label(output_frame, text="Estimated Range: ", fg=font_color, bg=frame_color, font=("Helvetica", 12, "bold"))
range_label.pack(pady=5)

# ----------------- Graph -----------------
fig, ax = plt.subplots(figsize=(6, 4))
fig.patch.set_facecolor(bg_color)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=20)

# ----------------- Style Configuration -----------------
style = ttk.Style()
style.configure("TLabelframe", background=frame_color, foreground=font_color, font=("Helvetica", 14, "bold"))
style.configure("TFrame", background=frame_color)
style.configure("TLabel", background=frame_color, foreground=font_color)

root.mainloop()
