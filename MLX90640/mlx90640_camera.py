# mlx90640_camera.py runs the IR sensor and displays the images in real
# time. For efficiency, this program displays the raw IR sensor readings,
# not converted to degrees.

import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

# initialize i2c bus
i2c = busio.I2C(board.SCL, board.SDA, frequency=1000000)
# initialize mlx attributes
mlx = adafruit_mlx90640.MLX90640(i2c)

#set refresh rate
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_16_HZ

#initialize data readings
frame = [0] * 768
t_array = []
#Initialize image
plt.ion()
mlx_shape = (24,32)
mlx_interp_val = 10# interpolate # on each dimension
mlx_interp_shape = (mlx_shape[0]*mlx_interp_val,
                    mlx_shape[1]*mlx_interp_val) # new shape


fig1, ax1 = plt.subplots()
array = np.zeros(shape=mlx_interp_shape, dtype=np.uint8)
axim1 = ax1.imshow(array, vmin=25, vmax=45,cmap=plt.cm.bwr)
cbar = fig1.colorbar(axim1) # setup colorbar
cbar.set_label('Temperature [$^{\circ}$F]',fontsize=14) # colorbar label

pix1 = []
def plot_update():
    mlx.getFrame(frame) # read mlx90640
    data = (np.reshape(frame,mlx_shape))*9/5+32 # reshape, flip data, conver to F
    
    data = ndimage.zoom(data,mlx_interp_val) # interpolate

    axim1.set_data((data))

    axim1.set_clim(vmin=80,vmax=np.max(data)) # set bounds
    plt.pause(0.001)
    fig1.canvas.flush_events()
while True:
    t1 = time.monotonic()
    try:
        plot_update()
    except ValueError:
        # these happen, no biggie - retry
        continue
    # approximating frame rate
    
    t_array.append(time.monotonic()-t1)
    if len(t_array)>10:
        t_array = t_array[1:] # recent times for frame rate approx
    #print('Frame Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))