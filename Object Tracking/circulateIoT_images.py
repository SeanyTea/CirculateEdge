from yolov5_tflite_image_inference import detect_image
import argparse
from glob import glob
import os

import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
from datetime import datetime 




def detect_from_folder_of_images(weights,folder_path,img_size,conf_thres,iou_thres,client):
    numFrames = 0
    for file in sorted(glob(f'{folder_path}/*.png'), key=lambda x: int(os.path.basename(x).split('_')[0])):
        print(file)
        print('Processing ',file,' now ...')
        
        detect_image(weights,folder_path,file,img_size,conf_thres,iou_thres,numFrames,client)
        numFrames +=1
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w','--weights', type=str, default='yolov5s-fp16.tflite', help='model.tflite path(s)')
    parser.add_argument('-f','--folder_path', type=str,required=True, help='folder path')  
    parser.add_argument('--img_size', type=int, default=416, help='image size') 
    parser.add_argument('--conf_thres', type=float, default=0.25, help='object confidence threshold')
    parser.add_argument('--iou_thres', type=float, default=0.45, help='IOU threshold for NMS')

    
    opt = parser.parse_args()
    

    myMQTTClient = AWSIoTMQTTClient("MacOS") #random key, if another connection using the same key is opened the previous one is auto closed by AWS IOT
    myMQTTClient.configureEndpoint("a2rhn7hbr9ksxp-ats.iot.us-east-1.amazonaws.com", 8883)

    myMQTTClient.configureCredentials("/Users/seanthammakhoune/Documents/AWS IoT Core/Mac/AmazonRootCA1.pem", "/Users/seanthammakhoune/Documents/AWS IoT Core/Mac/private_mac.pem.key", "/Users/seanthammakhoune/Documents/AWS IoT Core/Mac/certificate_mac.pem.crt")

    myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec

    print ('Initiating Realtime Data Transfer...')
    myMQTTClient.connect()

    detect_from_folder_of_images(opt.weights,opt.folder_path,opt.img_size,opt.conf_thres,opt.iou_thres,myMQTTClient)