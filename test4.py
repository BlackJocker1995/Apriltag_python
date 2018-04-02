import cv2
import numpy as np
import matplotlib.pyplot as plt
from tagfamilies import tag36h11
from TagDetection import TagDetection
def decodeQuad(images, quad):
    pass


def interpolate(p,uv):
    tmp0 = p[1,0,0] * p[2,0,1]
    tmp1 = p[2,0,0] * p[1,0,1]
    tmp2 = tmp0 - tmp1
    tmp3 = p[1,0,0] * p[3,0,1]
    tmp4 = tmp2 - tmp3
    tmp5 = p[3,0,0] * p[1,0,1]
    tmp6 = p[2,0,0] * p[3,0,1]
    tmp7 = p[3,0,0] * p[2,0,1]
    tmp8 = tmp4 + tmp5 + tmp6 - tmp7
    tmp9 = p[0,0,0] * p[2,0,0]
    tmp10 = tmp9 * p[1,0,1]
    tmp11 = p[1,0,0] * p[2,0,0]
    tmp12 = p[0,0,0] * p[3,0,0]
    tmp13 = p[1,0,0] * p[3,0,0]
    tmp14 = tmp13 * p[0,0,1]
    tmp15 = tmp9 * p[3,0,1]
    tmp16 = tmp13 * p[2,0,1]
    tmp17 = tmp10 - tmp11 * p[0,0,1] - tmp12 * p[1,0,1] + tmp14 - tmp15 + tmp12 * p[2,0,1] + tmp11 * p[3,0,1] - tmp16
    tmp18 = p[0,0,0] * p[1,0,0]
    tmp19 = p[2,0,0] * p[3,0,0]
    tmp20 = tmp18 * p[2,0,1] - tmp10 - tmp18 * p[3,0,1] + tmp14 + tmp15 - tmp19 * p[0,0,1] - tmp16 + tmp19 * p[1,0,1]
    tmp21 = p[0,0,0] * p[1,0,1]
    tmp22 = p[1,0,0] * p[0,0,1]
    tmp23 = tmp22 * p[2,0,1]
    tmp24 = tmp21 * p[3,0,1]
    tmp25 = p[2,0,0] * p[0,0,1]
    tmp26 = p[3,0,0] * p[0,0,1]
    tmp27 = tmp26 * p[2,0,1]
    tmp28 = tmp1 * p[3,0,1]
    tmp29 = tmp21 * p[2,0,1] - tmp23 - tmp24 + tmp22 * p[3,0,1] - tmp25 * p[3,0,1] + tmp27 + tmp28 - tmp5 * p[2,0,1]
    tmp30 = p[0,0,0] * p[2,0,1]
    tmp31 = tmp23 - tmp25 * p[1,0,1] - tmp24 + tmp26 * p[1,0,1] + tmp30 * p[3,0,1] - tmp27 - tmp0 * p[3,0,1] + tmp28
    tmp32 = p[0,0,0] * p[3,0,1]
    tmp33 = tmp30 - tmp25 - tmp32 - tmp0 + tmp1 + tmp26 + tmp3 - tmp5
    tmp34 = tmp21 - tmp22
    tmp35 = tmp34 - tmp30 + tmp25 + tmp3 - tmp5 - tmp6 + tmp7
    hx = (tmp17 / tmp8) * uv[0] - (tmp20 / tmp8) * uv[1] + p[0,0,0]
    hy = (tmp29 / tmp8) * uv[0] - (tmp31 / tmp8) * uv[1] + p[0,0,1]
    hw = (tmp33 / tmp8) * uv[0] + (tmp35 / tmp8) * uv[1] + 1
    return np.array([hy/hw,hx/hw])

def rotate90(w,d):
    wr = 0
    for r in range(d-1,-1,-1):
        for c in range(d):
            b = r + d * c
            wr = wr << 1
            if ((w & (1<<b)))!= 0:
                wr |= 1
    return wr


def decode(tagcode):
    tagcode = int(tagcode,16)
    d = 6
    bestid = -1
    besthamming = 255
    bestrotation = -1
    bestcode = -1
    rcodes = tagcode

    for r in range(4):
        index = 0
        for tag in tag36h11:
            dis = bin(tag^rcodes).count('1')
            if(dis < besthamming):
                besthamming = dis
                bestid = index
                #print (dis, index,besthamming)
                bestcode = tag
                bestrotation = r
            index+=1
        rcodes = rotate90(rcodes,d)
    tagdection = TagDetection()
    tagdection.id = bestid
    tagdection.hammingDistance = besthamming
    tagdection.obsCode = tagcode
    tagdection.matchCode = bestcode
    tagdection.rotation = bestrotation
    return tagdection


debug = False
filename = '3dpicture/0_0.jpg'
#filename = '3dpicture/1_4.jpg'
frame = cv2.imread(filename)
gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)


maxvalue = np.max(np.max(gray))
minvalue = np.min(np.min(gray))
img = gray
"""
1 blur
"""
img = cv2.GaussianBlur(img,(3,3),0.8)
"""
2 adaptive thresholding
"""
img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,9,5)
holdimg = img
if debug:
    plt.imshow(img)
    plt.gray()
    plt.show()
"""
3 find contours
"""
_,contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
quads = []
areas = []

"""
4 compute convex hulls and find maximum inscribed quadrilaterals
"""
for i in range(len(contours)):
    if (hierarchy[0,i,3] < 0 and contours[i].shape[0] >= 4):
        area = cv2.contourArea(contours[i])
        if area > 400:
            hull = cv2.convexHull(contours[i])
            if(area/cv2.contourArea(hull) > 0.8 ):
                quad = cv2.approxPolyDP(hull, 3, True)
                if(len(quad)==4):
                    areaqued = cv2.contourArea(quad)
                    areahull = cv2.contourArea(hull)
                    if areaqued/areahull  > 0.8 :
                     quads.append(quad)
if debug:
    cv2.drawContours(frame, quads, -1, (0, 255, 0), 2)
    plt.imshow(frame)
    plt.show()

"""
5 decode
"""
whiteBorder = 1
blackBorder = 1
points = []
for quad in quads:
    TagInfo = [36,11,len(tag36h11),tag36h11]
    dd = 2*blackBorder + 6#tagFamily.d
    blackvalue = []
    whitevalue = []
    tagcode = 0
    points = []
    for iy in range(dd):
        for ix in range(dd):
            x = (ix + 0.5) / dd
            y = (iy + 0.5) / dd
            point = np.int32(interpolate(quad, (x, y)))
            points.append(point)
            value = gray[point[0], point[1]]
            if ((iy == 0 or iy == dd-1) or (ix == 0 or ix == dd-1)):
                blackvalue.append(value)
            elif ((iy == 1 or iy == dd-2) or (ix == 1 or ix == dd-2)):
                whitevalue.append(value)
            else:
                continue
    if debug:
        points = np.array(points)
        plt.plot(points[:,1], points[:,0], 'rx')
        plt.imshow(gray)
        plt.gray()
        plt.show()
    threshold = (np.average(blackvalue) + np.average(whitevalue)) / 2
    for iy in range(dd):
        for ix in range(dd):
            if ((iy == 0 or iy == dd - 1) or (ix == 0 or ix == dd - 1)):
                continue
            x = (ix + 0.5) / dd
            y = (iy + 0.5) / dd
            point = np.int32(interpolate(quad, (x, y)))
            value = gray[point[0], point[1]]
            tagcode = tagcode << 1
            if value > threshold:
                tagcode |= 1
    tagcode = hex(tagcode)
    detection = decode(tagcode)
    for i in range(4):
        quad[(4+i-detection.rotation)%4] = quad[i]
    detection.points = quad
    print(detection.id,detection.hammingDistance)


