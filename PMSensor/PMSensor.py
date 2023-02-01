###########################################
# Created by The Machine Shop 2019        #
# Visit our website TheMachineShop.uk     #
# This script interfaces the Zio Qwiic    #
# PM2.5 Air Quality Sensor to a Raspberry #
# Pi over i2c and converts the data to    #
# micrograms per meter cubed	          #
# requires python-smbus to be installed:  #
# sudo apt-get install python-smbus       #
###########################################

# Import the required libraries
import time
import smbus

# Start the i2c bus and label as 'bus'
bus = smbus.SMBus(1)


start_time = time.time()
while True:
    if time.time()-start_time > 1:
        # Collect the data from the sensor
        data = bus.read_i2c_block_data(0x12, 0x00, 32)

        # Convert the collected data into the pm values
        PM1 = (data[4]<<8) + data[5]
        PM25 = (data[6]<<8) + data[7]
        PM10 = (data[8]<<8) + data[9]
        # Output the data to the terminal
        print ('Time: {:2f}, PM1.0: {:d}ug/m3, PM2.5: {:d}ug/m3, PM10: {:d}ug/m3'.format(time.time(),PM1, PM25, PM10))

        start_time = time.time()
