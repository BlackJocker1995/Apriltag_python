import cv2
import matplotlib.pyplot as plt
import tagFamilies as tf
import numpy as np
import time
from scipy import misc
from scipy import ndimage
class Apriltag(object):
    def __init__(self):
        self.tagfamily = None
        self.tagdetector = None

    def create_detector(self,family = 'tag36h11',sigma=0.8,nthread =1,debug = False,minarea = 400,thresholding = 'adaptive',downsampling = False):
        '''
        init what kind of tag you will detect
        '''
        self._downsampling = downsampling
        self._quad_sigma = sigma
        self._nthread = nthread
        self._minarea = minarea
        self._debug = debug
        self._thresholding = thresholding
        if(family == 'tag36h11'):
            self.tagfamily = tf.Tag36h11class(debug=self._debug)
        elif(family == 'tag25h9'):
            self.tagfamily = tf.Tag25h9class(debug = self._debug)
        elif(family == 'tag16h5'):
            self.tagfamily = tf.Tag16h5class(debug = self._debug)
        else:
            print("Do not support this tag")

    def detect(self,frame):
        gray = np.array(cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY))
        if self._downsampling:
            gray = misc.imresize(gray, [int(gray.shape[0] / 2), int(gray.shape[1] / 2)])
            gray = ndimage.zoom(gray,2,order=0)
        """
        1 blur
        """
        img = cv2.GaussianBlur(gray, (3, 3), self._quad_sigma)
        if (self._debug):
            plt.figure().set_size_inches(19.2,10.8)
            plt.imshow(img)
            plt.gray()
            plt.show()

        """
        2 adaptive thresholding or  canny
        """
        time_start = time.time()
        if(self._thresholding=='canny'):
            img = cv2.Canny(img,50,350,apertureSize=3)
            if(self._debug):
                print("Canny")
        elif(self._thresholding=='adaptive'):
            img = np.array(cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 9, 5),dtype='uint8')
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))
            img = cv2.morphologyEx(img, cv2.MORPH_OPEN,kernel)
#            img = cv2.GaussianBlur(img, (7, 7), self._quad_sigma)
            if (self._debug):
                print("Adaptive thresholding")

        else:
            if (self._debug):
                print("do not have this methon")


        ##################################
        time_end = time.time()
        if self._debug:
            print('preprocessor cost', time_end - time_start)
            plt.figure().set_size_inches(19.2, 10.8)
            plt.imshow(img)
            plt.gray()
            plt.show()
        ##################################

        """
        3 find contours
        """
        if (self._thresholding == 'canny'):
            contours, hierarchy = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        else:
            contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ##################################
        time_end = time.time()
        if self._debug:
            print(len(contours))
            print('contours cost', time_end - time_start)
        if self._debug:
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
                if area > self._minarea:
                    hull = cv2.convexHull(contours[i])
                    if (area / cv2.contourArea(hull) > 0.8):
                        if (self._debug):
                            hulls.append(hull)
                        quad = cv2.approxPolyDP(hull, 8, True)#maximum_area_inscribed
                        if (len(quad) == 4):
                            areaqued = cv2.contourArea(quad)
                            areahull = cv2.contourArea(hull)
                            if areaqued / areahull > 0.8 and areahull >= areaqued:
                                quads.append(quad)

        ##################################
        time_end = time.time()
        if self._debug:
            print('compute convex cost', time_end - time_start)
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