import os
import glob
import time
 
# Just in case load kernel modules to read the pins on raspberry
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
# Define the base directory for temperature sensor devices
base_dir = '/sys/bus/w1/devices/'

# Find the unique device folder starting with '28'. Temperature sensor DS18B20 typically starts with 28
device_folder = glob.glob(base_dir + '28*')[0]

# Define the path to the file containing temperature data
device_file = device_folder + '/w1_slave'

# Function to read raw temperature data from the sensor
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
# Function to read temperature from the sensor
def read_temp():
    lines = read_temp_raw()
    # Wait until the sensor indicates a valid reading
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    # Extract the temperature value from the raw data
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        # Convert temperature to Celsius
        temp_c = round(float(temp_string) / 1000.0, 2)

        return temp_c

