
'''Demonstrate Python wrapper of C apriltag library by running on camera frames.'''

from argparse import ArgumentParser
import cv2
import apriltag
import tagUtils as tud
import numpy as np
import  datetime
import apriltagpython as ap


def project(H,x,y):
    z = H[2,0]*x + H[2,1]*y +H[2,2];
    return [(H[0,0]*x+H[0,1]*y+H[0,2])/z,(H[1,0]*x+H[1,1]*y+H[1,2])/z]
def main():
    cap = cv2.VideoCapture(3)
    cap.set(3,1920)
    cap.set(4,1080)
    window = 'Camera'
    cv2.namedWindow(window)

    detector = ap.Apriltag()
    detector.create_detector(sigma=0.8, thresholding='canny', debug=False, downsampling=False)

    while cap.grab():
        success, frame = cap.retrieve()
        if not success:
            break
        starttime = datetime.datetime.now()
        detections = detector.detect(frame)
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
                point = tud.get_pose_point_noroate(detection.homography)
                dis = tud.get_distance(detection.homography,122274)
                for j in range(4):
                    cv2.line(show,tuple(point[edges[j,0]]),tuple(point[edges[j,1]]),(0,0,255))
                # dete_point = np.int32(detection.corners)
                # for j in range(4):
                #     cv2.line(show,
                #              tuple(dete_point[edges[j, 0]]),
                #              tuple(dete_point[edges[j, 1]]),
                #              color=(0,255,0))
                print ('dis:' , dis)

        ########################
        num_detections = len(detections)

        cv2.imshow(window, show)
        k = cv2.waitKey(1000)
        if k == 27:
            break
    cap.release()

if __name__ == '__main__':
    main()
