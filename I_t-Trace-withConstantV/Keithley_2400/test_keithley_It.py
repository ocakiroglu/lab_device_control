#!/usr/bin/env python3
import gpib
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.exporters import ImageExporter
import os
os.chdir(os.path.dirname(__file__))


# User parameters
keithley_address = 24    # GPIB address of the Keithley 2400
voltage = -10            # Voltage to perform I-t measurement in volts
v_ramp = 0.1             # Ramp time in seconds
ramping_delay = 0.1      # Delay between steps in seconds (min:0.05)
curr_comp = 3E-1         # Max Current which should be applied
curr_range = 10E-6       # Current Range
total_time = 75          # Total time for the measurement in seconds
verbose = True          # Do you want to display the data in real time? If yes, set to True.


###############################################################################
#########################    Main Program    ##################################

# Set the Communication
keithley = gpib.dev(0, keithley_address)  # use your GPIB address
gpib.write(keithley, "*IDN?\n")
keithley_byte = gpib.read(keithley, 1024)
print(keithley_byte.decode('utf-8').strip())  # Print the identification string

# Configure the Keithley 2400 for voltage sweep and current measurement: Manual_Page79
gpib.write(keithley, "*RST")  # Reset the instrument
gpib.write(keithley, ":SOUR:FUNC VOLT")  # Set source function to voltage
gpib.write(keithley, ":TRACe:CLEar")     # Clear the buffer before the measurement
gpib.write(keithley, ":SOUR:VOLT:MODE FIXED")
gpib.write(keithley, f":SENSe:CURRent:PROTection {curr_comp}")    # Set current compliance (adjust as needed)
gpib.write(keithley, f":SENS:CURR:RANG {curr_range}")
gpib.write(keithley, ":SENS:FUNC 'CURR'")  # Set measure function to current


# Enable output and start the sweep
gpib.write(keithley, ":OUTP ON")

if voltage > 0:
    for i in np.arange(0, voltage+v_ramp, v_ramp):
        gpib.write(keithley, f":SOUR:VOLT:LEV {i}")  # Set the voltage
        time.sleep(ramping_delay)
else:
    for i in np.arange(0, voltage-v_ramp, -v_ramp):
        gpib.write(keithley, f":SOUR:VOLT:LEV {i}")
        time.sleep(ramping_delay)


# Create a plot window using pyqtgraph
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
plot_widget.setLabel('bottom', 'Time (s)')
plot_widget.setTitle("<span style='font-size:24pt; color:k;'>I-t Measurement</span>")
plot_widget.showGrid(x=False, y=False)
if total_time <= 30:
    plot_widget.setXRange(0, total_time, padding=0.1)  # Set x-axis range from 0 to total_time
else:
    plot_widget.setXRange(0, 30, padding=0.1)

# Remove tick labels from right and top axes (keep ticks but hide labels)
right_axis = plot_widget.getAxis('right')
top_axis = plot_widget.getAxis('top')

# Store original ticks if needed
original_right_tickStrings = right_axis.tickStrings 
original_top_tickStrings = top_axis.tickStrings 

# Override tickStrings to return empty strings for right and top axes
right_axis.tickStrings = lambda values, scale, spacing: ['' for v in values]    
top_axis.tickStrings = lambda values, scale, spacing: ['' for v in values]

# Store the data
curr_list = np.array([])
time_list = np.array([])

# Create plot items with different styles
# Dataset 1: Red circles
curve = plot_widget.plot(
    time_list, curr_list,
    pen=None,             # No line connecting points
    symbol='o',           # Circle marker
    symbolBrush='r',      # Red color for marker fill
    symbolSize=8,
    name='Current'
)

#  Define the update function
def update_plot(new_x, new_y):
    # Use global to update the arrays outside the function
    global time_list, curr_list

    time_list = np.append(time_list, new_x)
    curr_list = np.append(curr_list, new_y)
    curve.setData(time_list, curr_list)

    if np.max(time_list) <= 30:
        plot_widget.setXRange(0, 30, padding=0.1)  # Set x-axis range from 0 to 30
    else:
        plot_widget.setXRange(np.max(time_list)-30, np.max(time_list), padding=0.1)
    plot_widget.update()


# Show the plot window before starting the update loop
win.show()
pg.QtWidgets.QApplication.processEvents()

# Start the measurement
gpib.write(keithley, ":SYSTem:TIME:RESet")  # Start the measurement
real_time = 0
while total_time > real_time:
    # Read the data, Convert to string, and split
    data_bytes = gpib.read(keithley, 100)
    try:
        data_string = data_bytes.decode('utf-8')
    except UnicodeDecodeError:
        data_string = data_bytes.decode('ascii', errors='ignore') # Try ASCII, ignoring errors if needed
    
    data = data_string.split(",")
    curr_data = float(data[1])
    real_time = float(data[3])

    # Update the plot data
    update_plot(real_time, curr_data)

    pg.QtWidgets.QApplication.processEvents()  # Ensure UI updates

    # Print the data
    if verbose:
        print(f"Time: {real_time:.4f} s \t\t Current: {curr_data} A")


# Calculate average time interval
diff_time = np.diff(time_list)
print(f"Average time interval: \t {np.mean(diff_time):.4f} seconds")

# Print the Number of Data Points
print(f"Number of data points: \t {len(curr_list)}")

# Turn off the output
gpib.write(keithley, ":OUTP OFF")

# Close the connection
gpib.close(keithley)

# Save data using numpy
data = np.column_stack((time_list, curr_list))
# Save the data with timestamp
timestamp = time.strftime("%Y%m%d-%H%M%S")
filename = f"current_time_data_{timestamp}"
np.savetxt(filename + ".txt", data, header="Time (s)\tCurrent (A)", delimiter="\t")

# Save the plot to a file using export functionality from PlotItem
exporter = pg.exporters.ImageExporter(plot_widget.plotItem)
exporter.export(filename + ".png")

print("The measurement was completed, the data was recorded and a graph was created.")

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
        all_x = np.concatenate([time_list])
        all_y = np.concatenate([curr_list])
        if all_x.size > 0:
            idx = (np.abs(all_x - x)).argmin()
            x_nearest = all_x[idx]
            y_nearest = all_y[idx]
            coord_label.setText(f"t={x_nearest:.2f}, I={y_nearest:.2e}")
            coord_label.setPos(x_nearest, y_nearest)
        else:
            coord_label.setText("")
            
proxy = pg.SignalProxy(plot_widget.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

# Create interactive window
pg.QtWidgets.QApplication.instance().exec()
