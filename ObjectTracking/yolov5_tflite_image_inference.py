from yolov5_tflite_inference import yolov5_tflite
import argparse
import cv2
import time
from pathlib import Path
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime 
from scipy import ndimage
import logging
import json

# limit the number of cpus used by high performance libraries
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 strongsort root directory
WEIGHTS = ROOT / 'weights'

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
if str(ROOT / 'yolov5') not in sys.path:
    sys.path.append(str(ROOT / 'yolov5'))  # add yolov5 ROOT to PATH
if str(ROOT / 'trackers' / 'strong_sort') not in sys.path:
    sys.path.append(str(ROOT / 'trackers' / 'strong_sort'))  # add strong_sort ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative


from PIL import Image
import numpy as np
from utils2 import letterbox_image, scale_coords
from trackers.multi_tracker_zoo import create_tracker

from scipy.interpolate import interp1d

def convertToMeters(xLoc,yLoc):
    xLeft = -1.27
    xRight = 1.3716
    yMax = 2.54
    yMin = 0

    xPixLeft = 0
    xPixRight = 320
    yPixMax = 240
    yPixMin = 0

    #Create a mapping function for x and y
    mX = interp1d([xPixLeft,xPixRight],[xLeft,xRight])
    mY = interp1d([yPixMin,yPixMax],[yMax,yMin])

    return float(mX(xLoc)), float(mY(yLoc))




def detect_image(weights,folder_path,image_url,img_size,conf_thres,iou_thres,numFrames,client):
    with open('class_names.txt') as f:
                names = [line.rstrip() for line in f]
    #Setup tracker
    reid_weights=WEIGHTS / 'osnet_x0_25_msmt17.pt'
    tracking_method='ocsort'
    device = 'cpu'
    half = False
    nr_sources = 1
    tracker_list = []
    for i in range(nr_sources):
        tracker = create_tracker(tracking_method, reid_weights, device, half)
        tracker_list.append(tracker, )
        if hasattr(tracker_list[i], 'model'):
            if hasattr(tracker_list[i].model, 'warmup'):
                tracker_list[i].model.warmup()
    outputs = [None] * nr_sources

    start_time = time.time()
    
    
    image = Image.open(image_url)
    original_size = image.size[:2]
    size = (img_size,img_size)
    image_resized = letterbox_image(image,size)
    img = np.asarray(image)
    
    image_array = np.asarray(image_resized)

    normalized_image_array = image_array.astype(np.float32) / 255.0


    yolov5_tflite_obj = yolov5_tflite(weights,img_size,conf_thres,iou_thres)

    result_boxes, result_scores, result_classes, result_class_names = yolov5_tflite_obj.detect(normalized_image_array)


    if len(result_boxes) > 0:
        result_boxes = np.array(result_boxes)
        result_scores = np.array([result_scores]).T
        result_class_names = np.array(result_classes)
        det = np.concatenate([result_boxes,result_scores,result_class_names],axis = 1)
        outputs[0] = tracker_list[0].update(det, image_array)

        #For drawing            
        # fontScale 
        fontScale = 0.5
            
        # Blue color in BGR 
        color = (255, 255, 0) 
        font = cv2.FONT_HERSHEY_SIMPLEX 
        # Line thickness of 1 px 
        thickness = 1
        #Tracker info and plotting
        if len(outputs[0]) > 0:
            for j, (output, conf) in enumerate(zip(outputs[0], det[:,:4])):
                data = {} #Data to be published
                bboxes = output[0:4]
                bboxes = scale_coords(size,np.array(bboxes),(original_size[1],original_size[0]))
                id = int(output[4])
                cls = output[5]
                c = int(cls)
                label = (f'{id} {names[c]}')
                if c == 1:
                    org = (int(bboxes[0][0]),int(bboxes[0][1]))
                    org2 = (int(bboxes[0][0]),int(bboxes[0][3]) + 12)
                    xLoc = (int(bboxes[0][0]) + int(bboxes[0][2]))// 2
                    yLoc = int(bboxes[0][3])
                    xLoc,yLoc = convertToMeters(xLoc,yLoc)
                    #Add to data
                    data['timestamp'] = datetime.now().strftime("%m_%d_%Y %H:%M:%S")
                    data['occupantID'] = id
                    data['x'] = round(xLoc,2)
                    data['y'] = round(yLoc,2) 
                    payloadMsg = json.dumps(data)
                    client.publish("HistoricalData",payloadMsg,1)
                    cv2.rectangle(img, (int(bboxes[0][0]),int(bboxes[0][1])), (int(bboxes[0][2]),int(bboxes[0][3])), (255,0,0), 1)
                    cv2.putText(img, "ID:"  + str(id) +  ', ' + str(int(100*result_scores[j])) + '%  ' + str(names[c]), org, font,  
                                fontScale, color, thickness, cv2.LINE_AA)
                    cv2.putText(img, "(%.2f, %.2f)"  % (xLoc,yLoc), org2, font,  
                                fontScale, color, thickness, cv2.LINE_AA)
                save_result_filepath = folder_path[:-11] + 'Annotated_offline'
                isExist = os.path.exists(save_result_filepath)
                if isExist == False:
                    os.makedirs(save_result_filepath)
                cv2.imshow('test',img[:,:,::-1])
                cv2.waitKey(1)
                img_to_save = Image.fromarray(img)
                img_to_save.save(save_result_filepath +'/' + str(image_url[80:]))
                #cv2.imwrite(save_result_filepath,img[:,:,::-1])
        font = cv2.FONT_HERSHEY_SIMPLEX 
        end_time = time.time()
        time.sleep(.33)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w','--weights', type=str, default='yolov5s-fp16.tflite', help='model.tflite path(s)')
    parser.add_argument('-i','--img_path', type=str, required=True, help='image path')  
    parser.add_argument('--img_size', type=int, default=416, help='image size')  
    parser.add_argument('--conf_thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou_thres', type=float, default=0.45, help='IOU threshold for NMS')

    
    opt = parser.parse_args()
    
    print(opt)
    detect_image(opt.weights,opt.img_path,opt.img_size,opt.conf_thres,opt.iou_thres)
