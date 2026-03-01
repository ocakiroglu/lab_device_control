# Current vs. Time (I-t) Measurement (Keithley 2400)

This directory contains Python automation scripts for performing **I-t Characterization** (Current sensing over a specific Time at a constant Voltage) using a **Keithley 2400 SourceMeter**.

The script provides a real-time visual interface for monitoring the measurement and automatically handles data logging.

<p align="center">
<img src="keithley2400.png" alt="Keithley 2400" height="220">
&nbsp;&nbsp;&nbsp;&nbsp;
<img src="GPIB-USB-HS_image.jpg" alt="GPIB-USB-HS interface" height="220">

<em>Figure 1: Keithley 2400 (Left) and National Instruments GPIB-USB-HS Interface (Right) </em>
</p>

## 🚀 Features

* **Soft Voltage Ramping:** Safely steps up to the target voltage before starting the measurement to protect your sample from sudden spikes.
* **Live Plotting:** Uses `pyqtgraph` for high-performance, real-time data visualization of the I-t curve.
* **Automated Export:** Saves data as a timestamped `.txt` (TSV) file and exports the final plot as a `.png`.
* **Interactive Inspection:** Includes a crosshair tool to inspect specific Time and Current values on the plot after the measurement concludes.

---

## 💾 Requirements

### a. Linux Requirements 🐧

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

Before running the script, open `test_keithley_It_v2.py` and adjust the parameters in the **User parameters** section:

| Parameter | Description |
| --- | --- |
| `keithley_address` | The GPIB address of the Keithley 2400 (Default 24) |
| `voltage` | The target constant voltage (in Volts) applied during the measurement |
| `v_ramp` | The voltage step size used to safely ramp up to the target voltage |
| `ramping_delay` | The delay (in seconds) between voltage steps during the initial ramp |
| `curr_comp` | Current compliance: The safety limit to prevent sample damage |
| `curr_range` | The fixed measurement range for the ammeter |
| `total_time` | The total duration (in seconds) for the measurement |
| `verbose` | Set to `True` to print real-time Time and Current values to the terminal |

---

## 📈 Usage

Run the script from the terminal:

```bash
python3 test_keithley_It_v2.py

```

or with any IDE (e.g., VS Code or Spyder) directly.

1. A window will appear showing the live I-t curve.
2. The current measurements are plotted in **Red** circles over time.
3. The X-axis automatically scrolls to track the latest data if the measurement exceeds **30 seconds**.
4. Once finished, the script will save a `.txt` file and a `.png` image in the same directory.
5. **Interactive Mode:** After the measurement, move your mouse over the plot to see specific Time and Current values.

## ⚠️ Safety Note

The script turns off the SourceMeter output (`:OUTP OFF`) when the full time duration completes. **Do not manually power off the Keithley while the output is ON unless in an emergency.**

*(Note: Unlike the I-V sweep script, this version does not currently intercept keyboard interruptions (Ctrl+C) to ramp the voltage back to zero. If you terminate the script early, the voltage may remain active.)*

## 🙏 Acknowledgments

* **Code Assistance:** This script was developed with the support of **GitHub Copilot**.
* **Institutional Support:** Developed at the **Universidad Complutense de Madrid (UCM)**.
* **Technical Guidance:** Driver installation procedures were adapted from the [Element14 Linux-GPIB Guide](https://community.element14.com/members-area/personalblogs/b/blog/posts/step-by-step-guide-how-to-use-gpib-with-raspberry-pi-linux).
