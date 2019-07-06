import cv2
from apriltag import Apriltag
import numpy as np
import tagUtils as tud
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
    ap.create_detector(debug=False,sigma=1.4,thresholding='canny',family='tag36h11')
    filename = '../3dpicture7/2_0.jpg'
    #filename = 'picture/1080p-30.jpg'
    frame = cv2.imread(filename)
    detections = ap.detect(frame)
    # show = frame
    # edges = np.array([[0, 1],
    #                   [1, 2],
    #                   [2, 3],
    #                   [3, 0]])
    # for detection in detections:
    #     point = tud.get_pose_point(detection.homography)
    #     for j in range(4):
    #         cv2.line(show, tuple(point[edges[j, 0]]), tuple(point[edges[j, 1]]), (0, 0, 255), 2)
    # cv2.imshow("Point", show)
    # k = cv2.waitKey(10000)
    # if k == 27:
    #     exit(0)
    print('total find:',len(detections))

