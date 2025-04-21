# MissileBoosterCode

## 🚀 Overview

This application is a user-friendly, professional-grade interface designed to calculate and visualize **multi-stage missile booster performance**. Built specifically for the United States Navy, the tool leverages aerospace-standard rocket equations to estimate **stage-by-stage delta-V (ΔV)** and **projected missile range** under customizable payload and booster configurations.

The tool uses the **Tsiolkovsky Rocket Equation** for realistic propulsion modeling and provides an intuitive interface for mission planners, propulsion engineers, and defense analysts to simulate launch configurations, evaluate propulsion stacks, and make rapid decisions in tactical and strategic environments.

---

## ⚙️ Features

- **3-Stage Rocket Modeling**  
  Calculates ΔV for each individual stage based on realistic mass and ISP inputs.

- **Visual Feedback**  
  Graphs stage-wise ΔV breakdown and total ΔV on a dark navy-themed professional plot.

- **Estimated Range Output**  
  Simplified range estimation based on total ΔV helps assess operational envelope.

- **Intuitive GUI**  
  Built with `Tkinter`, styled to meet military UX standards (large fonts, dark theme, spacing, etc.).

- **Modular Input**  
  Adjustable parameters: booster size, mass per stage, ISP, and geometric dimensions.

---

## 🧮 Underlying Physics

This system applies the **Tsiolkovsky Rocket Equation**: ΔV = Isp × g0 × ln(m0 / mf)

Where:
- `Isp` is specific impulse of the propellant (in seconds)
- `g0` is standard gravity (9.81 m/s²)
- `m0` and `mf` are the initial and final masses for each stage

Assumptions:
- Each stage has a propellant mass fraction (default: 80%)
- Total mass of a stage includes the remaining stages above it
- Flat Earth approximation for simplicity
- Same ISP for all stages (customizable)

---

## 🖥️ Usage Instructions

### 1. **Launch the Program**
Ensure Python and required libraries (`tkinter`, `matplotlib`) are installed. Then run:
```bash
python missile_booster_ui.py

### 2. **Enter Parameters**
You’ll see a clean Navy-themed user interface with labeled input fields. Fill in the following fields under "Input Parameters":

Booster Size (kg)
Enter the final payload mass (e.g., warhead or satellite).
Example: 250

Mass Stage 1 (kg)
Total mass of the first stage including propellant.
Example: 4000

Mass Stage 2 (kg)
Total mass of the second stage.
Example: 2500

Mass Stage 3 (kg)
Total mass of the third stage.
Example: 1500

Diameter (m)
Informational only; used for modeling or visual design.
Example: 1.0

Length (m)
Total length of the propulsion stack.
Example: 10.0

ISP (s)
Specific Impulse of the propulsion system (typical solid rockets = 250 s).
Example: 250


### 3. **Run Calculations**
Once all fields are filled:

Click the CALCULATE PERFORMANCE button at the center of the screen.

The software uses the Tsiolkovsky rocket equation to:

Calculate the delta-V (ΔV) for each stage

Calculate the total cumulative ΔV

Estimate the range based on ΔV

These results are displayed in real-time in the output panel.