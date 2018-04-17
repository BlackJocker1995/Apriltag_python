import numpy as np
import  cv2
import math
from scipy.optimize import fsolve
ss = 0.5
src = np.array([[-ss, -ss, 0],
                    [ss, -ss, 0],
                    [ss, ss, 0],
                    [-ss, ss, 0]])
#500 is scale
Kmat = np.array([[700, 0, 0],
                     [0, 700, 0],
                     [0, 0, 1]]) * 1.0
disCoeffs= np.zeros([4, 1]) * 1.0
edges = np.array([[0, 1],
                              [1, 2],
                              [2, 3],
                              [3, 0]])
def project(H,point):
    x = point[0]
    y = point[1]
    z = H[2,0]*x +H[2,1]*y+H[2,2]

    point[0] = (H[0,0]*x+H[0,1]*y+H[0,2])/z*1.0
    point[1] = (H[1, 0]*x+H[1, 1] *y + H[1, 2]) / z*1.0
    return point

def project_array(H):
    ipoints = np.array([[-1,-1],
                        [1,-1],
                        [1,1],
                        [-1,1]])
    for point in ipoints:
        point = project(H,point)

    return ipoints

def sovle_coord(R1,R2,R3,edge = 1060):
    x = -(R2*R2 - R1*R1 - edge**2) / (2.0*edge)
    y = -(R3*R3 - R1*R1 - edge**2) / (2.0*edge)
    z =  (np.sqrt(R1*R1 - x * x - y * y))-edge
    return x,y,z


def verify_z(x,y,R4,edge = 1060):
        x = edge - x
        y = edge - y
        rand2 = x**2+y**2
        h = np.sqrt(R4**2 - rand2)
        return edge - h


def get_Kmat(H):
    campoint = project_array(H)*1.0
    opoints = np.array([[-1.0, -1.0, 0.0],
                        [1.0, -1.0, 0.0],
                        [1.0, 1.0, 0.0],
                        [-1.0, 1.0, 0.0]])
    opoints = opoints*0.5
    rate, rvec, tvec = cv2.solvePnP(opoints, campoint, Kmat, disCoeffs)
    return rvec,tvec

def get_pose_point(H):
    """
    将空间坐标转换成相机坐标
    Trans the point to camera point
    :param H: homography
    :return:point
    """
    rvec, tvec =  get_Kmat(H)
    point, jac = cv2.projectPoints(src, rvec, tvec, Kmat, disCoeffs)
    return np.int32(np.reshape(point,[4,2]))

def get_pose_point_noroate(H):
    """
    将空间坐标转换成相机坐标但是不旋转
    Trans the point to camera point but no rotating
    :param H: homography
    :return:point
    """
    rvec, tvec = get_Kmat(H)
    point, jac = cv2.projectPoints(src, np.zeros(rvec.shape), tvec, Kmat, disCoeffs)
    return np.int32(np.reshape(point,[4,2]))

def average_dis(point,k):
    return np.abs( k/np.linalg.norm(point[0] - point[1]))
def average_pixel(point):
    return  np.abs( np.linalg.norm(point[0] - point[1]))
def get_distance(H,t):
    points = get_pose_point_noroate(H)
    return average_dis(points,t)
def get_min_distance(array_detections,t):
    min = 65535;
    for detection in array_detections:
        #print(detection.id)
        dis = get_distance(detection.homography,t)
        if dis < min:
            min = dis
    return min;

def get_pixel(H):
    points = get_pose_point_noroate(H)
    return average_pixel(points)

