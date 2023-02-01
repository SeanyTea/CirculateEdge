import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

directory = '/home/intelligentmedicine/Desktop/Thermal Sensor/examples/Pickle_Files_2D'
plt.ion()
mlx_shape = (24,32)
mlx_interp_val = 10# interpolate # on each dimension
mlx_interp_shape = (mlx_shape[0]*mlx_interp_val,
                    mlx_shape[1]*mlx_interp_val) # new shape


fig1, ax1 = plt.subplots()
ax1.axis('off')
array = np.zeros(shape=mlx_interp_shape, dtype=np.uint8)
axim1 = ax1.imshow(array, vmin=25, vmax=45,cmap=plt.cm.rainbow)

pix1 = []
def save_frame(frame,folder,cnt):
    data = (np.reshape(frame,mlx_shape))*9/5+32 # reshape, flip data, conver to F
    
    data = ndimage.zoom(data,mlx_interp_val) # interpolate

    axim1.set_data((data))

    axim1.set_clim(vmin=75,vmax=np.max(data)) # set bounds
    plt.savefig(folder +'/'+ str(cnt) + '.jpg')
cnt = 0
for file in os.listdir(directory):
    if file.endswith('.pkl'):
        with open(directory+ '/' + file, 'rb') as f:
            new_dir = directory +'/Images2/'+ file
            try:
                os.makedirs(new_dir)
            except:
                continue
                
            data = pickle.load(f)
            data_shape = np.shape(data)
            num_frames = data_shape[0]
            data = np.reshape(data,(num_frames,24,32))
            #num_frames =

            for i in range(num_frames):
                save_frame(data[i],new_dir,cnt)
                cnt +=1
