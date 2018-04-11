import cv2
from apriltagpython import Apriltag
import numpy as np
import tag_tuding as tud
from scipy.optimize import leastsq


def func(p,x):
    k,b = p
    return k*(x+b)
def error(p,x,y):
    return func(p,x)-y

def run():
    array = []
    xi = []
    detector = Apriltag()
    detector.create_detector(debug=False, sigma=1.4, thresholding='canny')
    for index in range(3, 16):
        filename = 'picture/1080p-' + str(index) + '0' + '.jpg'
        frame = cv2.imread(filename)
        detections = detector.detect(frame)

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
                xi.append(1 / dis)
                dete_point = np.int32(detection.points)
                array.append(dis * index * 100)
                print('pixeldis:', dis)

                ########################
                num_detections = len(detections)
    yi = np.array(range(300, 1600, 100)) * 1.0
    p0 = [1.0, 1.0]
    Para = leastsq(error, p0, args=(xi, yi))
    k, b = Para[0]
    print('y = ', k, 'x + ', b)
    print('average: ', np.average(array))

    caldis = []

    errors = []

    for index in range(3, 16):
        filename = 'picture/1080p-' + str(index) + '0' + '.jpg'
        frame = cv2.imread(filename)
        detections = detector.detect(frame)
        show = None
        if (len(detections) == 0):
            show = frame
        else:
            show = frame
            for detection in detections:
                dis = tud.get_distance(detection.homography, k)
                caldis.append(dis)
                print('dis:', dis)

    for i in range(12):
        errors.append((caldis[i + 1] - caldis[i]) / 100)
    arrayerror = np.average(errors)
    print('arrayerror  ', arrayerror)

if __name__ == '__main__':
    ap = Apriltag()
    ap.create_detector(debug=True,sigma=0.8,thresholding='canny',family='tag36h11')
    filename = '3dpicture/2_2.jpg'
    #filename = 'tag16.png'
    #filename = 'picture/1080p-30.jpg'
    frame = cv2.imread(filename)
    detections = ap.detect(frame)
    print('total find:',len(detections))

