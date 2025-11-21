import os
import xml.etree.ElementTree as ET
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

from .tagDetection import AprilTagDetection


def _load_tag_codes(family: str) -> List[int]:
    codes = []
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the XML file
    xml_file = os.path.join(script_dir, "tag_families", family + ".xml")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for code_h in root.findall("code_h"):
        if code_h.text is not None:
            codes.append(int(code_h.text, 16))
    return codes


class TagFamily(object):
    def __init__(
        self, tagcode: List[int], d: int, debug: bool = False, hammingdis: int = 3
    ) -> None:
        self._tagcode = tagcode
        self._d = d
        self._blackBorder = 1
        self._debug = debug
        self._hammingdis = hammingdis

    def _interpolate(
        self, p: np.ndarray, relativePoint: Tuple[float, float]
    ) -> np.ndarray:
        """
        calculate real points accoding relative points
        :param p: quad` four points
        :param relativePoint: relative points
        :return:
        """
        tmp0 = p[1, 0, 0] * p[2, 0, 1]
        tmp1 = p[2, 0, 0] * p[1, 0, 1]
        tmp2 = tmp0 - tmp1
        tmp3 = p[1, 0, 0] * p[3, 0, 1]
        tmp4 = tmp2 - tmp3
        tmp5 = p[3, 0, 0] * p[1, 0, 1]
        tmp6 = p[2, 0, 0] * p[3, 0, 1]
        tmp7 = p[3, 0, 0] * p[2, 0, 1]
        tmp8 = tmp4 + tmp5 + tmp6 - tmp7
        tmp9 = p[0, 0, 0] * p[2, 0, 0]
        tmp10 = tmp9 * p[1, 0, 1]
        tmp11 = p[1, 0, 0] * p[2, 0, 0]
        tmp12 = p[0, 0, 0] * p[3, 0, 0]
        tmp13 = p[1, 0, 0] * p[3, 0, 0]
        tmp14 = tmp13 * p[0, 0, 1]
        tmp15 = tmp9 * p[3, 0, 1]
        tmp16 = tmp13 * p[2, 0, 1]
        tmp17 = (
            tmp10
            - tmp11 * p[0, 0, 1]
            - tmp12 * p[1, 0, 1]
            + tmp14
            - tmp15
            + tmp12 * p[2, 0, 1]
            + tmp11 * p[3, 0, 1]
            - tmp16
        )
        tmp18 = p[0, 0, 0] * p[1, 0, 0]
        tmp19 = p[2, 0, 0] * p[3, 0, 0]
        tmp20 = (
            tmp18 * p[2, 0, 1]
            - tmp10
            - tmp18 * p[3, 0, 1]
            + tmp14
            + tmp15
            - tmp19 * p[0, 0, 1]
            - tmp16
            + tmp19 * p[1, 0, 1]
        )
        tmp21 = p[0, 0, 0] * p[1, 0, 1]
        tmp22 = p[1, 0, 0] * p[0, 0, 1]
        tmp23 = tmp22 * p[2, 0, 1]
        tmp24 = tmp21 * p[3, 0, 1]
        tmp25 = p[2, 0, 0] * p[0, 0, 1]
        tmp26 = p[3, 0, 0] * p[0, 0, 1]
        tmp27 = tmp26 * p[2, 0, 1]
        tmp28 = tmp1 * p[3, 0, 1]
        tmp29 = (
            tmp21 * p[2, 0, 1]
            - tmp23
            - tmp24
            + tmp22 * p[3, 0, 1]
            - tmp25 * p[3, 0, 1]
            + tmp27
            + tmp28
            - tmp5 * p[2, 0, 1]
        )
        tmp30 = p[0, 0, 0] * p[2, 0, 1]
        tmp31 = (
            tmp23
            - tmp25 * p[1, 0, 1]
            - tmp24
            + tmp26 * p[1, 0, 1]
            + tmp30 * p[3, 0, 1]
            - tmp27
            - tmp0 * p[3, 0, 1]
            + tmp28
        )
        tmp32 = p[0, 0, 0] * p[3, 0, 1]
        tmp33 = tmp30 - tmp25 - tmp32 - tmp0 + tmp1 + tmp26 + tmp3 - tmp5
        tmp34 = tmp21 - tmp22
        tmp35 = tmp34 - tmp30 + tmp25 + tmp3 - tmp5 - tmp6 + tmp7
        hx = (
            (tmp17 / tmp8) * relativePoint[0]
            - (tmp20 / tmp8) * relativePoint[1]
            + p[0, 0, 0]
        )
        hy = (
            (tmp29 / tmp8) * relativePoint[0]
            - (tmp31 / tmp8) * relativePoint[1]
            + p[0, 0, 1]
        )
        hw = (tmp33 / tmp8) * relativePoint[0] + (tmp35 / tmp8) * relativePoint[1] + 1
        return np.array([hy / hw, hx / hw])

    def _rotate_90(self, w: int, d: int) -> int:
        """
        rotate the code(bin) 90
        :param w: code(int)
        :param d: tag family`s d(edge length)
        :return: rotate 90 point
        """
        wr = 0
        for r in range(d - 1, -1, -1):
            for c in range(self._d):
                b = r + self._d * c
                wr = wr << 1
                if (w & (1 << b)) != 0:
                    wr |= 1
        return wr

    def _decode(self, tagcode: int, points: np.ndarray) -> AprilTagDetection:
        """
        decode the tagcode(int) and calculate distances between code you get and family`s code you own
        :param tagcode: tagcode (integer)
        :param points: quad(four point)
        :return:detection
        """
        bestid = -1
        besthamming = 255
        bestrotation = -1
        bestcode = -1
        rcodes = tagcode

        for r in range(4):
            index = 0
            for tag in self._tagcode:
                dis = bin(tag ^ rcodes).count("1")
                if dis < besthamming:
                    besthamming = dis
                    bestid = index
                    bestcode = tag
                    bestrotation = r
                index += 1
            rcodes = self._rotate_90(rcodes, self._d)
        tagdection = AprilTagDetection()
        tagdection.id = bestid
        tagdection.hammingDistance = besthamming
        tagdection.obsCode = tagcode
        tagdection.matchCode = bestcode
        tagdection.rotation = bestrotation
        if besthamming <= self._hammingdis:
            tagdection.good = True
            tagdection.add_point(points)
        return tagdection

    def decode_quad(
        self, quads: List[np.ndarray], gray: NDArray[np.uint8]
    ) -> List[AprilTagDetection]:
        """
        decode the Quad
        :param quads: array of quad which have four points
        :param gray: gray picture
        :return: array of detection
        """
        detections = []
        points = []
        whitepoint = []
        for quad in quads:
            dd = 2 * self._blackBorder + self._d
            blackvalue = []
            whitevalue = []
            tagcode = 0
            for iy in range(dd):
                for ix in range(dd):
                    x = (ix + 0.5) / dd
                    y = (iy + 0.5) / dd
                    point_coords = np.round(self._interpolate(quad, (x, y))).astype(
                        np.int32
                    )
                    point = (int(point_coords[0]), int(point_coords[1]))
                    points.append(point)
                    value = gray[point[0], point[1]]
                    if (iy == 0 or iy == dd - 1) or (ix == 0 or ix == dd - 1):
                        blackvalue.append(value)
                    elif (iy == 1 or iy == dd - 2) or (ix == 1 or ix == dd - 2):
                        whitevalue.append(value)
                    else:
                        continue
            threshold = (np.average(blackvalue) + np.average(whitevalue)) / 2
            for iy in range(dd):
                for ix in range(dd):
                    if (iy == 0 or iy == dd - 1) or (ix == 0 or ix == dd - 1):
                        continue
                    x = (ix + 0.5) / dd
                    y = (iy + 0.5) / dd
                    point_coords = np.round(self._interpolate(quad, (x, y))).astype(
                        np.int32
                    )
                    point = (int(point_coords[0]), int(point_coords[1]))
                    value = gray[point[0], point[1]]
                    tagcode = tagcode << 1
                    if value > threshold:
                        if self._debug:
                            whitepoint.append(point)
                        tagcode |= 1
            detection = self._decode(tagcode, quad)
            if detection.good:
                detection.add_homography()
                detections.append(detection)
        if self._debug and len(points) != 0:
            plt.figure().set_size_inches(19.2, 10.8)
            plt.subplot(121)
            showpoint = np.array(points)
            plt.plot(showpoint[:, 1], showpoint[:, 0], "rx")
            plt.imshow(gray)
            plt.gray()
            showpoint = np.array(whitepoint)
            plt.subplot(122)
            plt.plot(showpoint[:, 1], showpoint[:, 0], "rx")
            plt.imshow(gray)
            plt.gray()
            plt.show()
        return detections


class Tag36h11Family(TagFamily):
    def __init__(self, hammingdis: int = 3, debug: bool = False) -> None:
        super().__init__(_load_tag_codes("tag36h11"), 6, debug, hammingdis)


class Tag16h5Family(TagFamily):
    def __init__(self, hammingdis: int = 2, debug: bool = False) -> None:
        super().__init__(_load_tag_codes("tag16h5"), 4, debug, hammingdis)


class Tag25h9Family(TagFamily):
    def __init__(self, hammingdis: int = 2, debug: bool = False) -> None:
        super().__init__(_load_tag_codes("tag25h9"), 5, debug, hammingdis)
