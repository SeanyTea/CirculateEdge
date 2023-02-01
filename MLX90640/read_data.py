from datetime import datetime 

import time
import pickle
import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

with open('Pickle_Files_2D/data_11_21_2022_15:36:53.pkl','rb') as file:
    data = pickle.load(file)


plt.ion()
mlx_shape = (24,32)
mlx_interp_val = 10# interpolate # on each dimension
mlx_interp_shape = (mlx_shape[0]*mlx_interp_val,
                    mlx_shape[1]*mlx_interp_val) # new shape


fig1, ax1 = plt.subplots()
array = np.zeros(shape=mlx_interp_shape, dtype=np.uint8)
axim1 = ax1.imshow(array, vmin=25, vmax=45,cmap=plt.cm.rainbow)
cbar = fig1.colorbar(axim1) # setup colorbar
cbar.set_label('Temperature [$^{\circ}$F]',fontsize=14) # colorbar label

pix1 = []
def plot_update(frame):
    data = (np.reshape(frame,mlx_shape))*9/5+32 # reshape, flip data, conver to F
    
    data = ndimage.zoom(data,mlx_interp_val) # interpolate

    axim1.set_data((data))

    axim1.set_clim(vmin=78,vmax=np.max(data)) # set bounds
    plt.pause(0.001)
    fig1.canvas.flush_events()
'''
def plot_update(frame):

    #fig.canvas.restore_region(ax_background) # restore background

    data_array = np.flipud(np.fliplr(np.reshape(frame,(24,32)))) # reshape, flip data
    print(np.shape(data_array))
    axim1.set_array(data_array) # set data
    axim1.set_clim(vmin=np.min(data_array)+4,vmax=np.max(data_array)) # set bounds
    plt.pause(0.001)
    return
'''
data_shape = np.shape(data)
num_frames = data_shape[0]
#num_frames = 
for i in range(num_frames):
    plot_update(data[i])
