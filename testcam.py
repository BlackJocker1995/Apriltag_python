import cv2
from apriltagpython import myapriltag
import numpy as np
import tagUtils as tud
# ap = myapriltag()
# ap.createDetector(debug=True)
# #filename = '3dpicture/0_0.jpg'
# filename = 'picture/1080p-40.jpg'
# frame = cv2.imread(filename)
# detections = ap.detector(frame)
def main():
    cap = cv2.VideoCapture(0)
    cap.set(3,1920)
    cap.set(4,1080)
    fps = 24
    window = 'Camera'
    cv2.namedWindow(window)
    detector = myapriltag()
    detector.createDetector(debug=False)


    while cap.grab():
        success, frame = cap.retrieve()
        if not success:
            break

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
                point = tud.get_pose_point(detection.homography)
                dis = tud.get_distance(detection.homography,122274)
                for j in range(4):
                    cv2.line(show,tuple(point[edges[j,0]]),tuple(point[edges[j,1]]),(0,0,255),2)
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
        k = cv2.waitKey(1000//int(fps))

        if k == 27:
            break
    cap.release()

if __name__ == '__main__':
    main()

