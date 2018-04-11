import cv2
import apriltagpython as ap
import tag_tuding as tud
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
for index in range(0,5):
    filename = '3dpicture/0_'+ str(index)+'.jpg'
    filename1 = '3dpicture/1_' + str(index) + '.jpg'
    filename2 = '3dpicture/2_' + str(index) + '.jpg'
    filename3 = '3dpicture/3_' + str(index) + '.jpg'
    frame= cv2.imread(filename)
    frame1= cv2.imread(filename1)
    frame2= cv2.imread(filename2)
    frame3= cv2.imread(filename3)

    detector = ap.Apriltag()
    detector.create_detector(sigma = 1.4,thresholding='canny')

    detections = detector.detect(frame)
    detections1 = detector.detect(frame1)
    detections2 = detector.detect(frame2)
    detections3 = detector.detect(frame3)

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
