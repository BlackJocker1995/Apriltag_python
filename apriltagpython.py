import cv2
import matplotlib.pyplot as plt
import tagfamilies as tf
import numpy as np
import time
from scipy import misc
from scipy import ndimage
class myapriltag:
    def __init__(self):
        self.tagfamily = None
        self.tagdetector = None

    def createDetector(self,family = 'tag36h11',sigma=0.8,nthread =1,debug = False
                       ,minarea = 400,thresholding = 'adaptive'):

        self.quad_sigma = sigma
        self.nthread = nthread
        self.minarea = minarea
        self.debug = debug
        self.thresholding = thresholding
        if(family == 'tag36h11'):
            self.tagfamily = tf.tag36h11class(debug=self.debug)

    def detect(self,frame):
        gray = np.array(cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY))
        gray = misc.imresize(gray, [int(gray.shape[0] / 2), int(gray.shape[1] / 2)])
        gray = ndimage.zoom(gray,2,order=0)
        #gray = misc.imresize(gray, [int(gray.shape[0] * 2), int(gray.shape[1] * 2)])
        """
        1 blur
        """
        img = cv2.GaussianBlur(gray, (3, 3), self.quad_sigma)
        if (self.debug):
            plt.figure().set_size_inches(19.2,10.8)
            plt.imshow(img)
            plt.gray()
            plt.show()

        """
        2 adaptive thresholding or  canny
        """
        time_start = time.time()
        if(self.thresholding=='canny'):
            img = cv2.Canny(img,150,300,apertureSize=3)
            print("Canny")
        elif(self.thresholding=='adaptive'):
            img = np.array(cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 9, 5),dtype='uint8')
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
            img = cv2.morphologyEx(img, cv2.MORPH_OPEN,kernel)
            print("Adaptive thresholding")

        else:
            print("do not have this methon")


        ##################################
        time_end = time.time()
        print('preprocessor cost', time_end - time_start)
        if self.debug:
            plt.figure().set_size_inches(19.2, 10.8)
            plt.imshow(img)
            plt.gray()
            plt.show()
        ##################################

        """
        3 find contours
        """
        if (self.thresholding == 'canny'):
            _, contours, hierarchy = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        else:
            _, contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ##################################
        time_end = time.time()
        print(len(contours))
        print('contours cost', time_end - time_start)
        if self.debug:
            plt.figure().set_size_inches(19.2, 10.8)
            framecopy = np.copy(frame)
            cv2.drawContours(framecopy, contours, -1, (0, 255, 0), 2)
            plt.imshow(framecopy)
            plt.show()
        ##################################

        """
        4 compute convex hulls and find maximum inscribed quadrilaterals
        """
        quads = [] #array of quad including four peak points
        hulls = []
        for i in range(len(contours)):
            if (hierarchy[0, i, 3] < 0 and contours[i].shape[0] >= 4):
                area = cv2.contourArea(contours[i])
                if area > self.minarea:
                    hull = cv2.convexHull(contours[i])
                    if (area / cv2.contourArea(hull) > 0.8):
                        if (self.debug):
                            hulls.append(hull)
                        quad = cv2.approxPolyDP(hull, 3, True)#maximum_area_inscribed
                        if (len(quad) == 4):
                            areaqued = cv2.contourArea(quad)
                            areahull = cv2.contourArea(hull)
                            if areaqued / areahull > 0.8 and areahull >= areaqued:
                                quads.append(quad)

        ##################################
        time_end = time.time()
        print('compute convex cost', time_end - time_start)
        if self.debug:
            framecopy = np.copy(frame)
            cv2.drawContours(frame, quads, -1, (0, 255, 0), 2)
            cv2.drawContours(framecopy, hulls, -1, (0, 255, 0), 2)
            plt.figure().set_size_inches(19.2, 10.8)
            plt.subplot(211)
            plt.imshow(frame)
            plt.subplot(212)
            plt.imshow(framecopy)
            plt.show()
        ##################################
        """
        5 decode and get detections
        """
        return self.tagfamily.decodeQuad(quads,gray)