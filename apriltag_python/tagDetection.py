import cv2
import numpy as np


class AprilTagDetection(object):
    def __init__(self):
        self.good = False
        self.obsCode = -1
        self.matchCode = -1
        self.id = -1
        self.hammingDistance = -1
        self.rotation = -1
        self.points = None
        self.homography = None

    def add_homography(self):
        """
        find homography
        """
        self._recompute_homography()

    def add_point(self, points):
        """
        add quad`points to detection
        :param points: quad`s points
        """
        self.points = points

    def _recompute_homography(self):
        """
        find Homography
        :return: Homography
        """
        src = np.array(
            [
                [-1, -1],
                [1, -1],
                [1, 1],
                [-1, 1],
            ]
        ).reshape(-1, 1, 2)
        dst = np.array(self.points)
        retval, _ = cv2.findHomography(np.array(src), np.array(dst))
        dst = np.array(self.points)
        retval, _ = cv2.findHomography(np.array(src), np.array(dst))
        self.homography = retval
