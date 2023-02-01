#circulateIoT.py is the main file that will run our IoT processes.
# Begin with a passive run of the MLX90640 sensor. Every 30 seconds, print the time and date

import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime 
from scipy import ndimage
import numpy.core.multiarray
import cv2

#Set-up MLX90640 for future use
# initialize i2c bus
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
# initialize mlx attributes
mlx = adafruit_mlx90640.MLX90640(i2c)

#set refresh rate
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ

#initialize data readings
frame = [0] * 768
mlx_shape = (24,32)
mlx_interp_val = 10 # interpolate # on each dimension
def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)

#Function definitions
def convert_data(frame):
    data_array = np.reshape(frame,mlx_shape)*9/5+32 #Convert to F
    data_array = ndimage.zoom(data_array,mlx_interp_val)
    my_cm = plt.cm.get_cmap('rainbow')
    normed_data = (data_array - np.min(data_array)) / (np.max(data_array) - np.min(data_array))
    mapped_data = my_cm(data_array)
    mapped_data = mapped_data[:,:,:3] #Convert from RGBA to RGB
    mapped_data = mapped_data.transpose((0,1,2))[::-1] # HWC to CHW, keep as RGB
    mapped_data = letterbox(mapped_data, 640, 32, True)[0]  # padded resize

    return mapped_data

start_time = datetime.now()
print(start_time)
while True:
    try:
        tic = time.time()
        mlx.getFrame(frame)
        mapped_data = convert_data(frame)
        print(mapped_data.shape)
        toc = time.time()
        print(tic-toc)
    except ValueError:
        continue
    current_time = datetime.now()
    if (current_time-start_time).seconds == 30: #Every 30 seconds
        print(current_time)
        start_time = current_time #Reset start-time
