import cv2
import numpy as np
PATH = '/Users/seanthammakhoune/Documents/CirculateLogs/12_09_2022_15:53:06/Annotated_offline/'
# choose codec according to format needed
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
fps = 3.5 #weird...but keep 
img = []
for i in range(0,102): #Hard-code for now
	img.append(cv2.imread(PATH + str(i) + '_12_09_2022_15:53:06.png'))
height,width,layers=img[1].shape

video = cv2.VideoWriter('OSS2_Images_Detection.mp4',fourcc,fps,(width,height))
for j in range(len(img)):
	video.write(img[j])
cv2.destroyAllWindows()
video.release()