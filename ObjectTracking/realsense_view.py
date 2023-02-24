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

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 6)

advanced_mode = rs.rs400_advanced_mode(device)
json_file_path ='HighDensityPreset.json'
with open(json_file_path, 'r') as j:
    contents = json.loads(j.read())
json_string = str(contents).replace("'", '\"')

#advanced_mode.load_json(json_string)
# Start streaming
#config.enable_record_to_file('test.bag')
#config.enable_device_from_file('/home/intelligentmedicine/Desktop/CirculateEdge/ObjectTracking/test.bag')
pipeline.start(config)

numFrames = 1
start_time = time.time()

while True:

        #Obtain mlx frame
        
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            continue
    
        # Convert images to numpy arrays
        depth_frame = rs.decimation_filter(1).process(depth_frame)
        depth_frame = rs.disparity_transform(True).process(depth_frame)
        depth_frame = rs.spatial_filter().process(depth_frame)
        depth_frame = rs.temporal_filter().process(depth_frame)
        depth_frame = rs.disparity_transform(False).process(depth_frame)
        
        depth_image = np.asanyarray(depth_frame.get_data())
        print(depth_image)
        colorizer = rs.colorizer()
        colorizer.set_option(rs.option.visual_preset, 1) # 0=Dynamic, 1=Fixed, 2=Near, 3=Far
        colorizer.set_option(rs.option.min_distance, 1)
        colorizer.set_option(rs.option.max_distance, 5)
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())
        #depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        #depth_colormap = cv2.cvtColor(depth_colormap, cv2.COLOR_BGR2RGB)
        depth_colormap_dim = depth_colormap.shape
        # If depth and color resolutions are different, resize color image to match depth image for display
        '''
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))
        '''
        # Show images
        
        cv2.imshow('RealSense',depth_colormap)
        cv2.waitKey(1)
        '''
        img = Image.fromarray(depth_colormap)
        img.save('/home/intelligentmedicine/Desktop/TrainingImages/'+str(numFrames)+'.png')
        '''
        numFrames += 1
        print(numFrames)
        if time.time() - start_time > 30:
            
            pipeline.stop()
            break
        
