import cv2
from apriltag import Apriltag

ap = Apriltag()
ap.create_detector(debug=True)
filename = 'tag.png'
frame = cv2.imread(filename)
detections = ap.detect(frame)
if len(detections) > 0:
    print('识别成功')
else:
    print('识别失败')