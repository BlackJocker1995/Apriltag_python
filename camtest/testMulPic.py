import cv2
import apriltag as ap
import tagUtils as tud
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from mpl_toolkits.mplot3d import Axes3D
result = []
strname = '../3dpicture6'
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
    detector.create_detector(sigma=0.8,thresholding='adaptive',debug=False,downsampling=False)

    detections = detector.detect(frame)
    detections1 = detector.detect(frame1)
    detections2 = detector.detect(frame2)
    detections3 = detector.detect(frame3)

    show = None
    if (len(detections)<1 or len(detections1)<1 or len(detections2)<1 or len(detections3) < 1):
        continue
    else:
        tmp = 121938.0923
        add = 0
        dis = tud.get_min_distance(detections,tmp)+add
        dis1 = tud.get_min_distance(detections1, tmp)+add
        dis2 = tud.get_min_distance(detections2, tmp)
        dis3 = tud.get_min_distance(detections3,tmp)+add
        dege = 1000
        x, y ,z = tud.sovle_coord(dis,dis1,dis3,dege)
        x1, y1, z1 = tud.sovle_coord(dis3, dis, dis2,dege)
        x2,y2,z2 = tud.sovle_coord(dis2,dis3,dis1,dege)

        nz = tud.verify_z(x, y, dis2,dege)
        nz1 = tud.verify_z(x1, y1, dis1,dege)
        nz2 = tud.verify_z(x2,y2,dis,dege)

        x1,y1,nz1 = [y1,dege-x1,nz1]
        x2,y2,nz2 = [dege-x2,dege-y2,nz2]


        point = np.array([x,y,nz])
        point1 = np.array([x1, y1, nz1])
        point2 = np.array([x2, y2, nz2])


        print(point)
        print(point1)
        print(point2)
        print((point+point2+point1)/3)
        print()
        result.append((point+point2+point1)/3)
        ax = plt.subplot(111, projection='3d')
        ax.set_zlabel('z')
        ax.set_ylabel('y')
        ax.set_xlabel('x')
        ax.set_ylim(-200, 1200)
        ax.set_zlim(-200, 1200)
        ax.set_xlim(-200, 1200)
        ax.scatter(x, y, nz)
        ax.scatter(x1, y1, nz1)
        ax.scatter(x2, y2, nz2)
        plt.pause(0.001)
for i in range(len(result)-1,0,-1):
    print("sub: ",abs(abs(result[i][0] - result[i-1][0]) - 100))
