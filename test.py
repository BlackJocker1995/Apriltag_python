import cv2
from apriltag import Apriltag

ap = Apriltag()
ap.create_detector(debug=False)
filename = 'tag.png'
frame = cv2.imread(filename)
detections = ap.detect(frame)
if len(detections) > 0:
    print('识别成功')
    detections[0]._print()
else:
    print('识别失败')