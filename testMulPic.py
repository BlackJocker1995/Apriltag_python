import cv2
import apriltagpython as ap
import tagUtils as tud
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
result = []
strname = '../3dpicture'
for index in range(0,5):
    filename = strname+'/0_'+ str(index)+'.jpg'
    filename1 = strname+'/1_' + str(index) + '.jpg'
    filename2 = strname+'/2_' + str(index) + '.jpg'
    filename3 = strname+'/3_' + str(index) + '.jpg'
    frame= cv2.imread(filename)
    frame1= cv2.imread(filename1)
    frame2= cv2.imread(filename2)
    frame3= cv2.imread(filename3)

    detector = ap.Apriltag()
    detector.create_detector(sigma=0.8,thresholding='canny',debug=False,downsampling=False)

    detections = detector.detect(frame)
    detections1 = detector.detect(frame1)
    detections2 = detector.detect(frame2)
    detections3 = detector.detect(frame3)

    show = None
    if (len(detections)<1 or len(detections1)<1 or len(detections2)<1 or len(detections3) < 1):
        continue
    else:
        tmp = 121938.0923
        add = 30
        dis = tud.get_min_distance(detections,tmp)+add
        dis1 = tud.get_min_distance(detections1, tmp)+add
        dis2 = tud.get_min_distance(detections2, tmp)
        dis3 = tud.get_min_distance(detections3,tmp)+add

        x, y  = tud.sovle_coord(dis,dis1,dis3)

        nz = tud.verify_z(x, y, dis2)
        print(x,y,nz)
        result.append([x,y,nz])

for i in range(len(result)-1,0,-1):
    print("sub: ",abs(abs(result[i][0] - result[i-1][0]) - 100))
