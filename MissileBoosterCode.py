import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
from scipy.optimize import minimize

# Constants (will be modifiable in manual mode)
DIAMETER = 0.75
LENGTH = 7.5
PAYLOAD = 250
DENSITY = 1800
G0 = 9.81
RADIUS = DIAMETER / 2
AREA = math.pi * RADIUS**2
STRUCTURAL_COEFFS = [0.15, 0.10, 0.05]
total_propellant_mass = LENGTH * DENSITY * AREA

# Track the latest delta-V values for both rocket types
free_rocket_total_dv = 0
constrained_rocket_total_dv = 0

# Optimizer functions (unchanged)
def optimize_free_rocket(isp):
    ve = isp * G0
    def objective(x):
        m_p1, m_p2, m_p3 = x
        s1, s2, s3 = STRUCTURAL_COEFFS
        m0_3 = m_p3 * (1 + s3) + PAYLOAD
        mf_3 = m_p3 * s3 + PAYLOAD
        dv3 = ve * math.log(m0_3 / mf_3) if mf_3 > 0 else 0
        m0_2 = m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
        mf_2 = m_p2 * s2 + m_p3 * (1 + s3) + PAYLOAD
        dv2 = ve * math.log(m0_2 / mf_2) if mf_2 > 0 else 0
        m0_1 = m_p1 * (1 + s1) + m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
        mf_1 = m_p1 * s1 + m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
        dv1 = ve * math.log(m0_1 / mf_1) if mf_1 > 0 else 0
        return -(dv1 + dv2 + dv3)

    cons = ({'type': 'eq', 'fun': lambda x: sum(x) - total_propellant_mass})
    bounds = [(0, None)] * 3
    initial_guess = [total_propellant_mass/3] * 3
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=cons)
    return result.x if result.success else None

def optimize_constrained_rocket(isp, burn_time):
    ve = isp * G0
    total_burn_time = 30
    m_p1 = (burn_time / total_burn_time) * total_propellant_mass
    def objective(x):
        m_p2, m_p3 = x
        s1, s2, s3 = STRUCTURAL_COEFFS
        m0_3 = m_p3 * (1 + s3) + PAYLOAD
        mf_3 = m_p3 * s3 + PAYLOAD
        dv3 = ve * math.log(m0_3 / mf_3) if mf_3 > 0 else 0
        m0_2 = m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
        mf_2 = m_p2 * s2 + m_p3 * (1 + s3) + PAYLOAD
        dv2 = ve * math.log(m0_2 / mf_2) if mf_2 > 0 else 0
        m0_1 = m_p1 * (1 + s1) + m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
        mf_1 = m_p1 * s1 + m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
        dv1 = ve * math.log(m0_1 / mf_1) if mf_1 > 0 else 0
        return -(dv1 + dv2 + dv3)

    cons = ({'type': 'eq', 'fun': lambda x: m_p1 + x[0] + x[1] - total_propellant_mass})
    bounds = [(0, None)] * 2
    initial_guess = [total_propellant_mass/3] * 2
    result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=cons)
    return (m_p1, result.x[0], result.x[1]) if result.success else None

def calculate_free():
    if free_mode_var.get() == "Optimize":
        isp = float(free_entries["ISP (s)"].get())
        optimized_masses = optimize_free_rocket(isp)
        if optimized_masses is not None:
            for i in range(3):
                free_entries[f"Mass Stage {i+1} (kg)"].delete(0, tk.END)
                free_entries[f"Mass Stage {i+1} (kg)"].insert(0, f"{optimized_masses[i]:.2f}")
        update_outputs("free")
    else:  # Manual mode
        # Update global constants based on user input
        global PAYLOAD, DIAMETER, RADIUS, AREA
        PAYLOAD = float(free_entries["Payload Mass (kg)"].get())
        DIAMETER = float(free_entries["Diameter (m)"].get())
        RADIUS = DIAMETER / 2
        AREA = math.pi * RADIUS**2
        update_outputs("free")

    # Automatically update the constrained rocket's ΔV% loss when free rocket is calculated
    update_dv_loss()

def calculate_constrained():
    if constr_mode_var.get() == "Optimize":
        isp = float(constr_entries["ISP (s)"].get())
        burn_time = float(constr_entries["Burn Time Stage 1 (s)"].get())
        result = optimize_constrained_rocket(isp, burn_time)
        if result:
            constr_entries["Mass Stage 1 (kg)"].delete(0, tk.END)
            constr_entries["Mass Stage 1 (kg)"].insert(0, f"{result[0]:.2f}")
            for i in range(2):
                constr_entries[f"Mass Stage {i+2} (kg)"].delete(0, tk.END)
                constr_entries[f"Mass Stage {i+2} (kg)"].insert(0, f"{result[i+1]:.2f}")
        update_outputs("constrained")
    else:  # Manual mode
        # Update global constants based on user input
        global PAYLOAD, DIAMETER, RADIUS, AREA
        PAYLOAD = float(constr_entries["Payload Mass (kg)"].get())
        DIAMETER = float(constr_entries["Diameter (m)"].get())
        RADIUS = DIAMETER / 2
        AREA = math.pi * RADIUS**2
        update_outputs("constrained")

    # Always update the ΔV% loss calculation after constrained rocket is calculated
    update_dv_loss()

def update_dv_loss():
    global free_rocket_total_dv, constrained_rocket_total_dv

    # Ensure dv_loss_label is defined
    if dv_loss_label is None:
        return

    if free_rocket_total_dv > 0 and constrained_rocket_total_dv > 0:
        dv_diff = abs(free_rocket_total_dv - constrained_rocket_total_dv)
        dv_loss_percent = (dv_diff / free_rocket_total_dv) * 100
        dv_loss_label.config(text=f"ΔV% Loss: {dv_loss_percent:.2f}%")
    else:
        dv_loss_label.config(text="ΔV% Loss: Calculate both rockets first")

def update_outputs(rocket_type):
    global free_rocket_total_dv, constrained_rocket_total_dv

    entries = free_entries if rocket_type == "free" else constr_entries
    labels = free_delta_v_labels if rocket_type == "free" else constr_delta_v_labels
    total_label = free_total_delta_v_label if rocket_type == "free" else constr_total_delta_v_label
    range_lbl = free_range_label if rocket_type == "free" else constr_range_label
    bar_ax = free_bar_ax if rocket_type == "free" else constr_bar_ax
    line_ax = free_line_ax if rocket_type == "free" else constr_line_ax
    bar_canvas = free_bar_canvas if rocket_type == "free" else constr_bar_canvas
    line_canvas = free_line_canvas if rocket_type == "free" else constr_line_canvas

    isp = float(entries["ISP (s)"].get())
    m_p1 = float(entries["Mass Stage 1 (kg)"].get())
    m_p2 = float(entries["Mass Stage 2 (kg)"].get())
    m_p3 = float(entries["Mass Stage 3 (kg)"].get())
    ve = isp * G0
    s1, s2, s3 = STRUCTURAL_COEFFS

    m0_3 = m_p3 * (1 + s3) + PAYLOAD
    mf_3 = m_p3 * s3 + PAYLOAD
    dv3 = ve * math.log(m0_3 / mf_3) if mf_3 > 0 else 0

    m0_2 = m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
    mf_2 = m_p2 * s2 + m_p3 * (1 + s3) + PAYLOAD
    dv2 = ve * math.log(m0_2 / mf_2) if mf_2 > 0 else 0

    m0_1 = m_p1 * (1 + s1) + m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
    mf_1 = m_p1 * s1 + m_p2 * (1 + s2) + m_p3 * (1 + s3) + PAYLOAD
    dv1 = ve * math.log(m0_1 / mf_1) if mf_1 > 0 else 0

    total_dv = dv1 + dv2 + dv3
    estimated_range = total_dv * 0.5

    # Update global values to track for ΔV% loss calculation
    if rocket_type == "free":
        free_rocket_total_dv = total_dv
    else:
        constrained_rocket_total_dv = total_dv

    for i, dv in enumerate([dv1, dv2, dv3]):
        labels[i].config(text=f"Stage {i+1} ΔV: {dv:.2f} m/s")
    total_label.config(text=f"Total ΔV: {total_dv:.2f} m/s")
    range_lbl.config(text=f"Estimated Range: {estimated_range:.2f} km")

    # Update bar chart
    bar_ax.clear()
    bar_ax.bar(["Stage 1", "Stage 2", "Stage 3", "Total"], [dv1, dv2, dv3, total_dv],
           color=["#004080", "#0059b3", "#0073e6", "#00008B"])
    bar_ax.set_ylabel("ΔV (m/s)", fontsize=14, color="white")
    bar_ax.set_title("Stage-wise ΔV and Total ΔV", fontsize=16, color="white")
    bar_ax.tick_params(axis='x', labelsize=12, colors='white')
    bar_ax.tick_params(axis='y', labelsize=12, colors='white')
    bar_ax.set_facecolor('#0d1b2a')
    bar_canvas.draw()

    # Update line graph
    line_ax.clear()
    stage_masses = [m_p1, m_p2, m_p3]
    delta_vs = [dv1, dv2, dv3]

    # Create line graph
    line_ax.plot(stage_masses, delta_vs, 'o-', color='#0073e6', linewidth=2, markersize=8)

    # Add stage labels to each point
    for i, (mass, dv) in enumerate(zip(stage_masses, delta_vs)):
        line_ax.annotate(f"Stage {i+1}",
                    (mass, dv),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    color='white',
                    fontsize=12)

    line_ax.set_xlabel("Stage Mass (kg)", fontsize=14, color="white")
    line_ax.set_ylabel("ΔV (m/s)", fontsize=14, color="white")
    line_ax.set_title("Stage Mass vs ΔV", fontsize=16, color="white")
    line_ax.tick_params(axis='x', labelsize=12, colors='white')
    line_ax.tick_params(axis='y', labelsize=12, colors='white')
    line_ax.grid(True, linestyle='--', alpha=0.7, color='#415a77')
    line_ax.set_facecolor('#0d1b2a')
    line_canvas.draw()

def toggle_mode(rocket_type):
    if rocket_type == "free":
        mode = free_mode_var.get()
        entries = free_entries
        button = free_button
    else:
        mode = constr_mode_var.get()
        entries = constr_entries
        button = constr_button

    # Show/hide manual mode fields
    if mode == "Manual":
        # Update button text
        button.config(text=f"COMPUTE {rocket_type.upper()} ROCKET")

        # Show payload mass and diameter fields
        if "Payload Mass (kg)" in entries:
            entries["Payload Mass (kg)"].delete(0, tk.END)
            entries["Payload Mass (kg)"].insert(0, str(PAYLOAD))
            entries["Diameter (m)"].delete(0, tk.END)
            entries["Diameter (m)"].insert(0, str(DIAMETER))

        # Make payload and diameter fields visible
        manual_frames[rocket_type]["payload_frame"].pack(fill="x", padx=15, pady=8)
        manual_frames[rocket_type]["diameter_frame"].pack(fill="x", padx=15, pady=8)
    else:
        # Update button text
        button.config(text=f"OPTIMIZE {rocket_type.upper()} ROCKET")

        # Hide payload mass and diameter fields
        manual_frames[rocket_type]["payload_frame"].pack_forget()
        manual_frames[rocket_type]["diameter_frame"].pack_forget()

# GUI Setup
root = tk.Tk()
root.title("Missile Booster Performance - United States Navy")
root.geometry("1300x1000")
root.configure(bg="#0d1b2a")

style = ttk.Style()
style.configure("TFrame", background="#0d1b2a")
style.configure("TLabelframe", background="#1b263b", foreground="white", font=('Helvetica', 14, 'bold'))
style.configure("TLabel", background="#1b263b", foreground="white", font=('Helvetica', 14))
style.configure("TNotebook.Tab", font=('Helvetica', 14, 'bold'))
style.configure("TRadiobutton", background="#1b263b", foreground="white", font=('Helvetica', 12))

notebook = ttk.Notebook(root)
free_frame = ttk.Frame(notebook)
constr_frame = ttk.Frame(notebook)
notebook.add(free_frame, text="Free Rocket")
notebook.add(constr_frame, text="Constrained Rocket")
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Store manual mode frames for toggling visibility
manual_frames = {
    "free": {},
    "constrained": {}
}

# Global dv_loss_label variable to reference
dv_loss_label = None

def build_tab(tab_frame, tab_type):
    # Mode selection
    mode_frame = ttk.Frame(tab_frame)
    mode_frame.pack(fill="x", padx=30, pady=10)

    mode_var = tk.StringVar(value="Optimize")
    optimize_radio = ttk.Radiobutton(mode_frame, text="Optimize Mode", variable=mode_var,
                                     value="Optimize", command=lambda: toggle_mode(tab_type))
    optimize_radio.pack(side="left", padx=20)

    manual_radio = ttk.Radiobutton(mode_frame, text="Manual Mode", variable=mode_var,
                                   value="Manual", command=lambda: toggle_mode(tab_type))
    manual_radio.pack(side="left", padx=20)

    # Input parameters frame
    input_frame = ttk.LabelFrame(tab_frame, text="Input Parameters")
    input_frame.pack(padx=30, pady=15, fill="x")  # Changed from fill="both" to fill="x" to make it smaller

    entries = {}
    params = ["ISP (s)", "Mass Stage 1 (kg)", "Mass Stage 2 (kg)", "Mass Stage 3 (kg)"]
    if tab_type == "constrained":
        params.insert(1, "Burn Time Stage 1 (s)")

    for param in params:
        frame = ttk.Frame(input_frame)
        frame.pack(fill="x", padx=15, pady=5)  # Reduced pady from 8 to 5
        ttk.Label(frame, text=param).pack(side="left", padx=10)
        entry = ttk.Entry(frame, font=("Helvetica", 14), width=12)
        entry.pack(side="right", padx=10)
        entries[param] = entry

    # Manual mode additional fields (hidden by default)
    # Payload mass
    payload_frame = ttk.Frame(input_frame)
    ttk.Label(payload_frame, text="Payload Mass (kg)").pack(side="left", padx=10)
    payload_entry = ttk.Entry(payload_frame, font=("Helvetica", 14), width=12)
    payload_entry.pack(side="right", padx=10)
    payload_entry.insert(0, str(PAYLOAD))
    entries["Payload Mass (kg)"] = payload_entry
    manual_frames[tab_type]["payload_frame"] = payload_frame

    # Diameter
    diameter_frame = ttk.Frame(input_frame)
    ttk.Label(diameter_frame, text="Diameter (m)").pack(side="left", padx=10)
    diameter_entry = ttk.Entry(diameter_frame, font=("Helvetica", 14), width=12)
    diameter_entry.pack(side="right", padx=10)
    diameter_entry.insert(0, str(DIAMETER))
    entries["Diameter (m)"] = diameter_entry
    manual_frames[tab_type]["diameter_frame"] = diameter_frame

    # Default values
    entries["ISP (s)"].insert(0, "250")
    if "Burn Time Stage 1 (s)" in entries:
        entries["Burn Time Stage 1 (s)"].insert(0, "10")

    # Initial mass values - helpful for manual mode
    total_mass_per_stage = total_propellant_mass / 3
    entries["Mass Stage 1 (kg)"].insert(0, f"{total_mass_per_stage:.2f}")
    entries["Mass Stage 2 (kg)"].insert(0, f"{total_mass_per_stage:.2f}")
    entries["Mass Stage 3 (kg)"].insert(0, f"{total_mass_per_stage:.2f}")

    button = tk.Button(tab_frame,
                       text="OPTIMIZE " + tab_type.upper() + " ROCKET",
                       font=('Helvetica', 14, 'bold'),
                       bg="#00008B", fg="white",
                       command=calculate_constrained if tab_type == "constrained" else calculate_free)
    button.pack(pady=10)  # Reduced from 15 to 10

    output_frame = ttk.LabelFrame(tab_frame, text="Outputs")
    output_frame.pack(padx=30, pady=5, fill="x")  # Changed from fill="both" to fill="x", reduced pady

    delta_labels = []
    for i in range(3):
        lbl = tk.Label(output_frame, text=f"Stage {i+1} ΔV: ", font=("Helvetica", 14), fg="white", bg="#1b263b")
        lbl.pack(pady=2)  # Reduced from 3 to 2
        delta_labels.append(lbl)

    total_lbl = tk.Label(output_frame, text="Total ΔV: ", font=("Helvetica", 14, "bold"), fg="white", bg="#1b263b")
    total_lbl.pack(pady=2)  # Reduced from 3 to 2

    range_lbl = tk.Label(output_frame, text="Estimated Range: ", font=("Helvetica", 14, "bold"), fg="white", bg="#1b263b")
    range_lbl.pack(pady=2)  # Reduced from 3 to 2

    # Only add ΔV% loss label for constrained rocket
    if tab_type == "constrained":
        global dv_loss_label
        dv_loss_label = tk.Label(output_frame, text="ΔV% Loss: Calculate both rockets first",
                                 font=("Helvetica", 14, "bold"), fg="#ff9900", bg="#1b263b")
        dv_loss_label.pack(pady=2)

    # Create charts frame to hold both charts side by side
    charts_frame = ttk.Frame(tab_frame)
    charts_frame.pack(fill="both", expand=True, padx=30, pady=10)

    # Left chart (Bar chart)
    left_chart_frame = ttk.Frame(charts_frame)
    left_chart_frame.pack(side="left", fill="both", expand=True)

    bar_fig, bar_ax = plt.subplots(figsize=(5, 4))
    bar_fig.patch.set_facecolor('#0d1b2a')
    bar_ax.set_facecolor('#0d1b2a')
    bar_canvas = FigureCanvasTkAgg(bar_fig, master=left_chart_frame)
    bar_canvas.get_tk_widget().pack(fill="both", expand=True)

    # Right chart (Line graph)
    right_chart_frame = ttk.Frame(charts_frame)
    right_chart_frame.pack(side="right", fill="both", expand=True)

    line_fig, line_ax = plt.subplots(figsize=(5, 4))
    line_fig.patch.set_facecolor('#0d1b2a')
    line_ax.set_facecolor('#0d1b2a')
    line_canvas = FigureCanvasTkAgg(line_fig, master=right_chart_frame)
    line_canvas.get_tk_widget().pack(fill="both", expand=True)

    return entries, delta_labels, total_lbl, range_lbl, bar_ax, bar_canvas, line_ax, line_canvas, mode_var, button

# Build both tabs
free_entries, free_delta_v_labels, free_total_delta_v_label, free_range_label, free_bar_ax, free_bar_canvas, free_line_ax, free_line_canvas, free_mode_var, free_button = build_tab(free_frame, "free")
constr_entries, constr_delta_v_labels, constr_total_delta_v_label, constr_range_label, constr_bar_ax, constr_bar_canvas, constr_line_ax, constr_line_canvas, constr_mode_var, constr_button = build_tab(constr_frame, "constrained")

# Hide manual mode fields initially
toggle_mode("free")
toggle_mode("constrained")

# Add button to force update the ΔV% loss calculation
def force_update_dv_loss():
    # This ensures both values are properly read from the UI before calculation
    global free_rocket_total_dv, constrained_rocket_total_dv

    # Extract the total ΔV values from the labels
    free_dv_text = free_total_delta_v_label.cget("text")
    constr_dv_text = constr_total_delta_v_label.cget("text")

    # Parse the numbers from the label text
    try:
        free_rocket_total_dv = float(free_dv_text.split(": ")[1].split(" ")[0])
        constrained_rocket_total_dv = float(constr_dv_text.split(": ")[1].split(" ")[0])

        # Calculate and update the ΔV% loss
        dv_diff = abs(free_rocket_total_dv - constrained_rocket_total_dv)
        dv_loss_percent = (dv_diff / free_rocket_total_dv) * 100
        dv_loss_label.config(text=f"ΔV% Loss: {dv_loss_percent:.2f}%")
    except (IndexError, ValueError):
        dv_loss_label.config(text="ΔV% Loss: Calculate both rockets first")


root.mainloop()