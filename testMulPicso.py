import cv2
import apriltag
import tagUtils as tud
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
strname = '../3dpicture1'
for index in range(0,5):
    filename = strname+'/0_'+ str(index)+'.jpg'
    filename1 = strname+'/1_' + str(index) + '.jpg'
    filename2 = strname+'/2_' + str(index) + '.jpg'
    filename3 = strname+'/3_' + str(index) + '.jpg'
    frame= cv2.imread(filename)
    frame1= cv2.imread(filename1)
    frame2= cv2.imread(filename2)
    frame3= cv2.imread(filename3)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
    gray3 = cv2.cvtColor(frame3, cv2.COLOR_RGB2GRAY)
    window = 'Camera'
    cv2.namedWindow(window)

    detector = apriltag.Detector()

    detections = detector.detect(gray, return_image=False)
    detections1 = detector.detect(gray1, return_image=False)
    detections2 = detector.detect(gray2, return_image=False)
    detections3 = detector.detect(gray3, return_image=False)

    show = None
    if (len(detections)+len(detections1)+len(detections2)+len(detections3) < 4):
        continue
    else:
        dis = tud.get_distance(detections[0].homography,122274.9)
        dis1 = tud.get_distance(detections1[0].homography, 122274.9)
        dis2 = tud.get_distance(detections2[0].homography, 122274.9)
        dis3 = tud.get_distance(detections3[0].homography, 122274.9)

        x, y, z  = tud.sovle_coord(dis,dis1,dis3)

        z = tud.verify_z(x, y, dis2)

        print(x, y, z)
