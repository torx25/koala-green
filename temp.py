import os
import glob
import time
import datetime
from datetime import date
from time import strftime
import csv

# Initialize the GPIO Pins
os.system('modprobe w1-gpio')  # Turns on the GPIO module
os.system('modprobe w1-therm') # Turns on the Temperature module

# Finds the correct device file that holds the temperature data
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# A function that reads the sensors data
def read_temp_raw():
    f = open(device_file, 'r') # Opens the temperature device file
    lines = f.readlines() # Returns the text
    f.close()
    return lines

# Convert the value of the sensor into a temperature
def read_tempc():
    lines = read_temp_raw() # Read the temperature 'device file'

    # While the first line does not contain 'YES', wait for 0.2s
    # and then read the device file again.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    # Look for the position of the '=' in the second line of the
    # device file.
    equals_pos = lines[1].find('t=')

    # If the '=' is found, convert the rest of the line after the
    # '=' into degrees Celsius, then degrees Fahrenheit
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c0 = float(temp_string) / 1000.0
        temp_c = '{0:.3f}'.format(temp_c0) # to 3 decimal places
        return temp_c

def read_tempf():
    lines = read_temp_raw() # Read the temperature 'device file'

    # While the first line does not contain 'YES', wait for 0.2s
    # and then read the device file again.
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    # Look for the position of the '=' in the second line of the
    # device file.
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f0 = temp_c * 9.0 / 5.0 + 32.0
        temp_f = '{0:.3f}'.format(temp_f0) # to 3 decimal places
        return temp_f

# Print out and log the temperature until the program is stopped.
with open("/home/pi/temp_log.csv", "a") as log:
    i = 0
    if os.stat("/home/pi/temp_log.csv").st_size == 0:
        log.write("DateTime,Delta,TempC,TempF\n")
    while True:
        i += 1
        if i == 1:
            start_time0 = (datetime.datetime.now()).replace(microsecond=0)
        cur_time = (datetime.datetime.now()).replace(microsecond=0)
        delta = '{0:.3f}'.format(((cur_time - start_time0).total_seconds())/60)
        tempc = str(read_tempc())
        tempf = str(read_tempf())
        print(str(i) + ' ' + str(delta) + ' ' + str(cur_time.strftime("%Y-%m-%d %H:%M:%S")) + ' Temp = ' + str(tempc) + '°C / ' + str(tempf) + '°F')
        # Append data to the csv
        log.write("{0},{1},{2},{3}\n".format(str(cur_time.strftime("%Y-%m-%d %H:%M:%S")),str(delta),str(tempc),str(tempf)))
        time.sleep(1)
