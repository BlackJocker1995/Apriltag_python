import cv2
import numpy as np
import apriltag
import tagUtils as tud
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
class Multcamdet(object):
    def __init__(self,n,debug = False):
        self.n = n
        self.videocaptures = []
        self.videowrite = []
        self.frames = []
        self.debug = debug
        self.detector = apriltag.Apriltag().create_detector()
        self.__filename = []

    def __create_videocapture(self):
        """
        初始化videocapture
        :return:None
        """
        for i in range(self.n):
            cap = cv2.VideoCapture()
            flag = cap.open(i)
            cap.set(3, 1920)
            cap.set(4, 1080)
            if(flag):
                self.videocaptures.append(cap)
            else:
                print(i ," not open")
                exit(1)

    def __create_videowrite(self):
        """
        初始化videowriter
        :return: None
        """
        for i in range(self.n):
            out = cv2.VideoWriter(str(i)+'.avi',cv2.cv.CV_FOURCC('m','p','4','v'),10,(1920,1080))
            self.videowrite.append(out)

    def __create_fileRead(self):
        """
        批量读入文件
        :return:
        """
        for index in range(self.n):
            filename = '3dpicture/'+str(index)+'_'
            self.__filename.append(filename)

    def __get_grad(self):
        """
        批量获取相机帧
        get grad using cam
        :return:
        """
        for capture in self.videocaptures:
            flag = capture.grab()
            if(flag==False):
                return False
        return True

    def __get_frame(self):
        """
        批量抓取图像
        :return:
        """
        for capture in self.videocaptures:
            flag,frame = capture.retrieve()
            if flag:
                self.frames.append(frame)
            else:
                print ('can`t get frame')

    def __get_picture(self,index):
        """
        读入对应index的批量图像
        :param index:
        :return:
        """
        for i in range(self.n):
            frame = cv2.imread(self.__filename[i]+str(index)+'.jpg')
            self.frames.append(frame)

    def __save_frame_avi(self):
        for cap,out in zip(self.videocaptures,self.videowrite):
            flag,frame = cap.retrieve()
            if flag:
                out.write(frame)
            else:
                print ('can`t get frame')

    def __detector_id_dis(self):
        result = []
        cam = 0
        for frame in self.frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            detections = self.detector.detect(gray)
            num_detections = len(detections)
            if (num_detections == 0):
                continue
            else:
                distances = np.zeros(num_detections)
                tagid = np.zeros(num_detections)
                i = 0
                for detection in detections:
                    dis = tud.get_distance(detection.homography,121938.1)
                    distances[i] = dis
                    tagid[i] = detection.tag_id
                    i = i + 1
                min_index = np.argmin(distances)
                result.append([cam,tagid[min_index], distances[min_index]])
            cam = cam+1
        self.frames = []  # clear
        return np.array(result)


    def detectormult_four_pic(self,num):
        self.__create_fileRead()
        ax = plt.subplot(111, projection='3d')
        ax.set_zlabel('z')
        ax.set_ylabel('y')
        ax.set_xlabel('x')
        ax.set_ylim(-20, 120)
        ax.set_zlim(-20, 120)
        ax.set_xlim(-20, 120)
        for index in range(num):
            self.__get_picture(index)
            result = self.__detector_id_dis()
            if len(result) == 4:
                x, y, z = tud.sovle_coord(result[0, 2], result[1, 2], result[3, 2], edge=1100)
                R4 = result[2, 2]
                z = tud.verify_z(x, y, R4)
                ax.scatter(x, y, z)
                print(x, y, z)


    def save_four_video(self):
        self.__create_videocapture()
        self.__create_videowrite()
        while(self.__get_grad()):
            self.__save_frame_avi()
            k = cv2.waitKey(100/10)
            print('save')
            if k == 5:
                break
        for out in self.videowrite:
            out.release()
    def detectormult(self):
        self.__create_videocapture()

        while(self.__get_grad()):
            self.__get_frame()
            result = self.__detector_id_dis()
            #print result
            if(len(result)==3):
                aux =  tud.sovle_coord(result[2,2],result[0,2],result[1,2])
                print( aux )
                plt.subplot(111, projection='3d')
                plt.scatter(aux[0], aux[1], aux[2])
                plt.scatter(25, 58, 3)
                plt.pause(0.001)
                #plt.clf()
    def detectormult_four(self):
        self.__create_videocapture()

        while (self.__get_grad()):
            self.__get_frame()
            result = self.__detector_id_dis()
            ax = plt.subplot(111, projection='3d')

            #fig.canvas.mpl_connect("key_press_event",self.on_key_press)
            ax.set_zlabel('z')
            ax.set_ylabel('y')
            ax.set_xlabel('x')
            ax.set_ylim(-200,1200)
            ax.set_zlim(-200, 1200)
            ax.set_xlim(-200, 1200)
            if len(result)==4:
                x,y,z = tud.sovle_coord(result[0, 2], result[1, 2], result[3, 2],edge=1100)
                R4 = result[2,2]
                z = tud.verify_z(x,y,R4)
                ax.scatter(x, y, z)
                print(x,y,z)
            plt.pause(0.001)

    def __del__(self):
        for cap in self.videocaptures:
            cap.release()


def main():
   camdet = Multcamdet(4)
   camdet.detectormult_four()

if __name__ == '__main__':
    main()