import cv2
import apriltag
import tagUtils as tud
import numpy as np
import datetime
import matplotlib.pyplot as plt
from scipy.optimize import leastsq

def func(p,x):
    k,b = p
    return k*(x+b)
def error(p,x,y):
    return func(p,x)-y


array = []
xi = []
for index in range(3,16):
    filename = 'picture/1080p-'+ str(index) +'0'+'.jpg'
    frame = cv2.imread(filename)
    window = 'Camera'
    cv2.namedWindow(window)
    detector = apriltag.Detector()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    starttime = datetime.datetime.now()
    detections = detector.detect(gray, return_image=False)
    endtime = datetime.datetime.now()
    #print (endtime-starttime)

    show = None
    if (len(detections) == 0):
        show = frame
    else:
        show = frame
        edges = np.array([[0, 1],
                              [1, 2],
                              [2, 3],
                              [3, 0]])

        for detection in detections:
            dis = tud.get_pixel(detection.homography)
            xi.append(1/dis)
            dete_point = np.int32(detection.corners)
            array.append(dis*index*100)
            print 'dis:' , dis

            ########################
            num_detections = len(detections)
yi = np.array(range(300,1600,100))*1.0
p0 = [1.0,1.0]
Para = leastsq(error,p0,args=(xi,yi))
k,b = Para[0]
print('y = ',k,'x + ',b)
print 'average: ',np.average(array)


caldis = []

errors = []

for index in range(3,16):
    filename = 'picture/1080p-'+ str(index) +'0'+'.jpg'
    frame = cv2.imread(filename)
    window = 'Camera'
    cv2.namedWindow(window)
    detector = apriltag.Detector()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    starttime = datetime.datetime.now()
    detections = detector.detect(gray, return_image=False)
    endtime = datetime.datetime.now()

    show = None
    if (len(detections) == 0):
        show = frame
    else:
        show = frame
        for detection in detections:
            dis = tud.get_distance(detection.homography,k)
            caldis.append(dis)
            print 'dis:' , dis


for i in range(12):
    errors.append((caldis[i+1] - caldis[i])/100)
arrayerror = np.average(errors)
print ('arrayerror  ',arrayerror)


