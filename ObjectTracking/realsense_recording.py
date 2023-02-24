import pyrealsense2 as rs
import json
import time
import cv2
import numpy as np
from PIL import Image

pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

depth_sensor = device.first_depth_sensor()
## Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_scale = depth_sensor.get_depth_scale()


found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 15)

advanced_mode = rs.rs400_advanced_mode(device)
json_file_path ='HighDensityPreset.json'
with open(json_file_path, 'r') as j:
    contents = json.loads(j.read())
json_string = str(contents).replace("'", '\"')

#advanced_mode.load_json(json_string)
# Start streaming
timestr = time.strftime("%Y%m%d-%H%M%S")
config.enable_record_to_file('UrbanCoworks_' +timestr+ '.bag')
#config.enable_device_from_file('/home/intelligentmedicine/Desktop/CirculateEdge/ObjectTracking/test3.bag')
pipeline.start(config)

numFrames = 1
start_time = time.time()

while True:

        #Obtain mlx frame
        
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame:
            continue
        
        print(numFrames)
        if time.time() - start_time > 360:
            print("Stopping...")
            pipeline.stop()
            break
        

