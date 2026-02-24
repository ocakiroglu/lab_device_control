#!/usr/bin/python
import gpib
import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters
import time
import os
os.chdir(os.path.dirname(__file__))


# Define the voltage sweep parameters
keithley_address = 24    # GPIB address of the Keithley 2400
start_voltage = -5.0     # Start voltage in volts
stop_voltage = 5.0       # Stop voltage in volts
step_voltage = 0.25       # Step size in volts 
delay = 0.05             # Delay between steps in seconds (min:0.05)
curr_comp = 1.05         # Max Current which should be applied (min:1E-6 , max: 1.05A)
curr_range = 1E-6         # Current Range (min:1E-6 , max: 1.05A)
file_suffix = None       # File name suffix for saving data, if None, it will not be used
verbose = False          # Do you want to display the data in real time? If yes, set to True.


###############################################################################
#########################    Main Program    ##################################

# Set the Communication
keithley = gpib.dev(0, keithley_address)  # use your GPIB address
gpib.write(keithley, "*IDN?\n")
keithley_byte = gpib.read(keithley, 1024)
print(keithley_byte.decode('utf-8').strip())  # Print the identification string


# Configure the Keithley 2400 for voltage sweep and current measurement
gpib.write(keithley, "*RST")  # Reset the instrument
gpib.write(keithley, ":SOUR:FUNC VOLT")  # Set source function to voltage
gpib.write(keithley, ":TRACe:CLEar")     # Clear the buffer before the measurement
gpib.write(keithley, ":SOUR:VOLT:MODE FIXED")
gpib.write(keithley, f":SENSe:CURRent:PROTection {curr_comp}")    # Set current compliance (adjust as needed)
gpib.write(keithley, f":SENS:CURR:RANG {curr_range}")
gpib.write(keithley, ":SENS:FUNC 'CURR'")  # Set measure function to current


# Enable output and start the sweep
gpib.write(keithley, ":OUTP ON")


# Create volt_list for the voltage sweep 0 to -stop_voltage, -stop_voltage to stop_voltage, and stop_voltage to 0
# Round the data to 2 decimal places
volt_list1 = np.arange(0, -stop_voltage-step_voltage, -step_voltage)
volt_list2 = np.arange(-stop_voltage, stop_voltage+step_voltage, step_voltage)
volt_list3 = np.arange(stop_voltage, 0-step_voltage, -step_voltage)
volt_list = np.concatenate((volt_list1, volt_list2, volt_list3))

# Round the volt_list to 2 decimal places
volt_list = np.round(volt_list, 2)

# Determine min and max voltage
v_min = np.min(volt_list)
v_max = np.max(volt_list)


# Set up the plotting window
app = pg.QtWidgets.QApplication([])
win = pg.QtWidgets.QMainWindow()
win.setWindowTitle('Live Data Plotting with PyQtGraph')
win.setGeometry(100, 100, 1200, 800)
plot_widget = pg.PlotWidget()
win.setCentralWidget(plot_widget)

# Show right and top axis
plot_widget.showAxis('right')
plot_widget.showAxis('top')


# Increase the font size of x and y labels and set axis/tick color to black
font = pg.QtGui.QFont()
font.setPointSize(18)
for axis in ['left', 'bottom', 'right', 'top']:
    ax = plot_widget.getAxis(axis)
    if ax is not None:
        ax.setTickFont(font)
        ax.setPen(pg.mkPen(color='k', width=2))  # Axis line and ticks in black
        ax.setTickPen(pg.mkPen(color='k', width=2))
        ax.setTextPen(pg.mkPen(color='k'))       # Tick labels in black
        ax.setLabel(ax.labelText, units=ax.labelUnits, **{'font-size': '18pt', 'color': 'k'})
        if axis == 'left':
            # Use a lambda to format y-axis ticks in scientific notation
            ax.setStyle(autoExpandTextSpace=True, tickTextOffset=10, showValues=True)
            ax.tickStrings = lambda values, scale, spacing: [f"{v:.2e}" for v in values]

# Change the background color to white
plot_widget.setBackground('w')

# Add a legend to the plot
legend = plot_widget.addLegend()
legend.setBrush(pg.mkBrush(color=(10, 10, 10, 10)))

# Set axis labels and title (no need to set size here, handled above)
plot_widget.setLabel('left', 'Current (A)')
plot_widget.setLabel('bottom', 'Voltage (V)')
plot_widget.setTitle("<span style='font-size:24pt; color:k;'>I-V Measurement</span>")
plot_widget.showGrid(x=False, y=False)
plot_widget.setXRange(v_min + v_min*0.05, v_max*1.05)


# Remove tick labels from right and top axes (keep ticks but hide labels)
right_axis = plot_widget.getAxis('right')
top_axis = plot_widget.getAxis('top')

# Store original ticks if needed
original_right_tickStrings = right_axis.tickStrings 
original_top_tickStrings = top_axis.tickStrings 

# Override tickStrings to return empty strings for right and top axes
right_axis.tickStrings = lambda values, scale, spacing: ['' for v in values]    
top_axis.tickStrings = lambda values, scale, spacing: ['' for v in values]

# Initialize data arrays
x_data1 = np.array([])
y_data1 = np.array([])

x_data2 = np.array([])
y_data2 = np.array([])

# Create plot items with different styles
# Dataset 1: Red circles
curve1 = plot_widget.plot(
    x_data1, y_data1,
    pen=None,             # No line connecting points
    symbol='o',           # Circle marker
    symbolBrush='r',      # Red color for marker fill
    symbolSize=8,
    name='Forward'
)

# Dataset 2: Blue squares
curve2 = plot_widget.plot(
    x_data2, y_data2,
    pen=None,             # No line connecting points
    symbol='o',           # Square marker
    symbolBrush='b',      # Blue color for marker fill
    symbolSize=8,
    name='Backward'
)


# --- 5. Define the update function ---
def update_plot(new_x, new_y, direction):
    # Use global to update the arrays outside the function
    global x_data1, y_data1, x_data2, y_data2

    if direction == "forward":
        x_data1 = np.append(x_data1, new_x)
        y_data1 = np.append(y_data1, new_y)
        curve1.setData(x_data1, y_data1)
    else:
        x_data2 = np.append(x_data2, new_x)
        y_data2 = np.append(y_data2, new_y)
        curve2.setData(x_data2, y_data2)

    plot_widget.setXRange(v_min + v_min*0.05, v_max*1.05)
    plot_widget.update()

# Show the plot window before starting the update loop
win.show()
pg.QtWidgets.QApplication.processEvents()


# Perform the sweep and measure current
voltages = np.zeros(len(volt_list))
currents = np.zeros(len(volt_list))

try:
    for i, voltage in enumerate(volt_list):
        gpib.write(keithley, f":SOUR:VOLT:LEV {voltage}")  # Set the voltage
        time.sleep(delay)  # Wait for the measurement to stabilize
        
        # Read the data, Convert to string, and split
        data_bytes = gpib.read(keithley, 100)
        try:
            data_string = data_bytes.decode('utf-8')
        except UnicodeDecodeError:
            data_string = data_bytes.decode('ascii', errors='ignore') # Try ASCII, ignoring errors if needed

        data = data_string.split(",")
        curr_data = float(data[1])
        volt_data = float(data[0])

        # Store the data
        voltages[i] = volt_data
        currents[i] = curr_data

        # Update the plot with the new data
        if i < len(volt_list1):  # Backward voltage
            update_plot(volt_data, curr_data, "backward")
        elif i < len(volt_list1) + len(volt_list2):  # Forward voltage
            update_plot(volt_data, curr_data, "forward")
        else:  # Backward voltage again
            update_plot(volt_data, curr_data, "backward")
        
        pg.QtWidgets.QApplication.processEvents()  # Ensure UI updates

        # Print the data if verbose is True
        if verbose:
            print(f" Voltage: {volt_data} V \t Current: {curr_data} A")

except KeyboardInterrupt:
    print("\nMeasurement interrupted by user.")
except Exception as e:
    print(f"Error during measurement: {e}")
finally:
    # Ensure voltage is ramped to zero regardless of how the loop exits
    print("Ramping voltage back to zero...")
    try:
        # Get the current voltage from the last successful measurement
        if 'volt_data' in locals():
            current_voltage = volt_data
        else:
            current_voltage = 0  # Default to 0 if no measurement was completed
            
        if abs(current_voltage) > 0.01:  # Only ramp if voltage is not already close to zero
            ramp_steps = max(int(abs(current_voltage) / step_voltage), 1)
            ramp_voltages = np.linspace(current_voltage, 0, ramp_steps + 1)[1:]  # Exclude current voltage
            
            for ramp_voltage in ramp_voltages:
                gpib.write(keithley, f":SOUR:VOLT:LEV {ramp_voltage}")
                time.sleep(delay)
                if verbose:
                    print(f"Ramping voltage: {ramp_voltage:.2f} V")
        
        # Final set to exactly zero
        gpib.write(keithley, ":SOUR:VOLT:LEV 0")
        time.sleep(delay)
        print("Voltage ramped to zero.")
        
        # Turn off the output
        gpib.write(keithley, ":OUTP OFF")
        
    except Exception as e:
        print(f"Error during voltage ramp: {e}")
        # Still try to turn off output even if ramping fails
        try:
            gpib.write(keithley, ":OUTP OFF")
        except:
            pass
    
    # Close the connection
    try:
        gpib.close(keithley)
    except:
        pass


# Save data using numpy
data = np.column_stack((voltages, currents))
# Save the data with timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")
if file_suffix:
    filename = f"voltage_sweep_data_{timestamp}_{file_suffix}"
else:
    filename = f"voltage_sweep_data_{timestamp}"
np.savetxt(filename + ".txt", data, header="Voltage (V)\tCurrent (A)", delimiter="\t")

# Save the plot to a file using export functionality from PlotItem
exporter = pg.exporters.ImageExporter(plot_widget.plotItem)
exporter.export(filename + ".png")

print("Sweep completed, data saved, and plot generated.")

# Add a crosshair and a label to show data coordinates on mouse hover
vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('g', width=1))
hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('g', width=1))
plot_widget.addItem(vLine, ignoreBounds=True)
plot_widget.addItem(hLine, ignoreBounds=True)
coord_label = pg.TextItem("", anchor=(0,1), color='k')
plot_widget.addItem(coord_label)

def mouseMoved(evt):
    pos = evt[0]  # using signal proxy turns original arguments into a tuple
    if plot_widget.sceneBoundingRect().contains(pos):
        mousePoint = plot_widget.plotItem.vb.mapSceneToView(pos)
        x = mousePoint.x()
        y = mousePoint.y()
        vLine.setPos(x)
        hLine.setPos(y)
        # Find the closest data point in either curve
        all_x = np.concatenate([x_data1, x_data2])
        all_y = np.concatenate([y_data1, y_data2])
        if all_x.size > 0:
            idx = (np.abs(all_x - x)).argmin()
            x_nearest = all_x[idx]
            y_nearest = all_y[idx]
            coord_label.setText(f"V={x_nearest:.2f}, I={y_nearest:.2e}")
            coord_label.setPos(x_nearest, y_nearest)
        else:
            coord_label.setText("")
            
proxy = pg.SignalProxy(plot_widget.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

# Create interactive window
pg.QtWidgets.QApplication.instance().exec()

