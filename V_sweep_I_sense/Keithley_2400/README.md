# Voltage Sweeping - Current Sensing (Keithley 2400)

This directory contains Python automation scripts for performing **I-V Characterization** (Voltage Sweeps while sensing Current) using a **Keithley 2400 SourceMeter**.

The script provides a real-time visual interface for monitoring the sweep and automatically handles data logging and safety procedures.

<p align="center">
  <img src="keithley2400.png" alt="Keithley 2400" height="220">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="GPIB-USB-HS_image.jpg" alt="GPIB-USB-HS interface" height="220">
  <br>
  <em>Figure 1: Keithley 2400 (Left) and National Instruments GPIB-USB-HS Interface (Right) </em>
</p>

## 🚀 Features

* **Bi-Directional Sweeping:** Automatically performs a $0V \rightarrow -V_{min} \rightarrow +V_{max} \rightarrow 0V$ loop.
* **Live Plotting:** Uses `pyqtgraph` for high-performance, real-time data visualization.
* **Safety Ramping:** If the script is interrupted (Ctrl+C) or hits an error, it automatically ramps the voltage back to $0V$ to protect your equipment and sample.
* **Automated Export:** Saves data as a timestamped `.txt` (TSV) file and exports the final plot as a `.png`.
* **Interactive Inspection:** Includes a crosshair tool to inspect specific data points on the plot after the sweep.

---
## 💾 Requirements

###  a. Linux Requirements 🐧

This script is designed for **Linux** environments. Because National Instruments (NI) does not officially support the **GPIB-USB-HS** interface on modern Linux distributions, you must use the open-source **linux-gpib** driver.

For a complete, step-by-step guide on compiling and installing these drivers, please refer to: 👉 [Detailed Linux-GPIB Installation Guide](https://github.com/ocakiroglu/lab_device_control/blob/main/V_sweep_I_sense/Keithley_2400/install_linux_gpib.md)

### b. Python Dependencies 🐍

Install the required Python packages via `pip`:

```bash
pip install numpy pyqtgraph PyQt5

```

> **Note:** Although there is no `import pyqt5` directly in the script, having `pyqtgraph` requires a Qt backend like `PyQt5`.

---

### c. Permission 🔑

By default, Linux restricts access to the GPIB interface. You must run the following command every time you plug in the device or restart your computer to grant the necessary permissions:

```bash
sudo chmod 666 /dev/gpib0

```

---

## 🛠 Configuration

Before running the script, open `test_keithley_IV.py` and adjust the parameters in the **Main Program** section:

| Parameter | Description |
| --- | --- |
| `keithley_address` | The GPIB address of the Keithley 2400 (Default 24) |
| `min_voltage` | The negative peak (minimum voltage) of the sweep |
| `max_voltage` | The positive peak (maximum voltage) of the sweep |
| `step_voltage` | The voltage increment/decrement between measurements |
| `curr_comp` | Current compliance: The safety limit to prevent sample damage |
| `curr_range` | The fixed measurement range for the ammeter |

---

## 📈 Usage

Run the script from the terminal:

```bash
python3 test_keithley_IV.py

```

or any IDE (eg: VS Code or Spyder) directly. 

1. A window will appear showing the live I-V curve.
2. The "Forward" sweep is marked in **Red**, and the "Backward" sweep in **Blue**.
3. Once finished, the script will save a `.txt` file and a `.png` image in the same directory.
4. **Interactive Mode:** After the sweep, move your mouse over the plot to see specific Voltage and Current values.

## ⚠️ Safety Note

The script includes a `finally` block that ensures the SourceMeter output is disabled and the voltage is set to $0V$ upon exit. **Do not manually power off the Keithley while the output is ON unless in an emergency.**
