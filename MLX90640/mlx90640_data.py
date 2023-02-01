# mlx90640_data.py saves the raw frame data
from datetime import datetime 
from datetime import datetime 

import time
import pickle
import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt

#For data saving
FULL_PATH = '/home/intelligentmedicine/Desktop/Thermal Sensor/examples/Pickle_Files_2D/'
now = datetime.now()
time_str = now.strftime("%m_%d_%Y %H:%M:%S")
name_list = time_str.split(' ')
file_name = FULL_PATH + 'data_'+ name_list[0] + '_'+name_list[1] + '.pkl'
# initialize i2c bus
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
# initialize mlx attributes
mlx = adafruit_mlx90640.MLX90640(i2c)

#set refresh rate
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ

#initialize data readings
frame = [0] * 768
t_array = []
shape = (24,32)

data = []
start_time = datetime.now()
i = 0
while (datetime.now()-start_time).seconds <= 2:
    print("waiting")
start_time = datetime.now()
while (datetime.now()-start_time).seconds <= 10:
    t1 = time.monotonic()
    try:
        mlx.getFrame(frame)
        
    except ValueError:
        # these happen, no biggie - retry
        continue
    # approximating frame rate
    data.append(np.array(frame).T)
    t_array.append(time.monotonic()-t1)
    if len(t_array)>10:
        t_array = t_array[1:] # recent times for frame rate approx
    print('Frame Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
    

with open(file_name,'wb') as file:
    pickle.dump(data[1:],file)