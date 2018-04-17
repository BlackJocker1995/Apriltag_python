import numpy as np
import matplotlib.pyplot as plt
from tagDetection import TagDetection


class Tagclass(object):

    def __init__(self,tagcode,d,debug=False,hammingdis=3):
        self._tagcode = tagcode
        self._d = d
        self._blackBorder = 1
        self._debug = debug
        self._hammingdis = hammingdis

    def _interpolate(self,p, relativePoint):
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
        tmp17 = tmp10 - tmp11 * p[0, 0, 1] - tmp12 * p[1, 0, 1] + tmp14 - tmp15 + tmp12 * p[2, 0, 1] + tmp11 * p[
            3, 0, 1] - tmp16
        tmp18 = p[0, 0, 0] * p[1, 0, 0]
        tmp19 = p[2, 0, 0] * p[3, 0, 0]
        tmp20 = tmp18 * p[2, 0, 1] - tmp10 - tmp18 * p[3, 0, 1] + tmp14 + tmp15 - tmp19 * p[0, 0, 1] - tmp16 + tmp19 * \
                p[1, 0, 1]
        tmp21 = p[0, 0, 0] * p[1, 0, 1]
        tmp22 = p[1, 0, 0] * p[0, 0, 1]
        tmp23 = tmp22 * p[2, 0, 1]
        tmp24 = tmp21 * p[3, 0, 1]
        tmp25 = p[2, 0, 0] * p[0, 0, 1]
        tmp26 = p[3, 0, 0] * p[0, 0, 1]
        tmp27 = tmp26 * p[2, 0, 1]
        tmp28 = tmp1 * p[3, 0, 1]
        tmp29 = tmp21 * p[2, 0, 1] - tmp23 - tmp24 + tmp22 * p[3, 0, 1] - tmp25 * p[3, 0, 1] + tmp27 + tmp28 - tmp5 * p[
            2, 0, 1]
        tmp30 = p[0, 0, 0] * p[2, 0, 1]
        tmp31 = tmp23 - tmp25 * p[1, 0, 1] - tmp24 + tmp26 * p[1, 0, 1] + tmp30 * p[3, 0, 1] - tmp27 - tmp0 * p[
            3, 0, 1] + tmp28
        tmp32 = p[0, 0, 0] * p[3, 0, 1]
        tmp33 = tmp30 - tmp25 - tmp32 - tmp0 + tmp1 + tmp26 + tmp3 - tmp5
        tmp34 = tmp21 - tmp22
        tmp35 = tmp34 - tmp30 + tmp25 + tmp3 - tmp5 - tmp6 + tmp7
        hx = (tmp17 / tmp8) * relativePoint[0] - (tmp20 / tmp8) * relativePoint[1] + p[0, 0, 0]
        hy = (tmp29 / tmp8) * relativePoint[0] - (tmp31 / tmp8) * relativePoint[1] + p[0, 0, 1]
        hw = (tmp33 / tmp8) * relativePoint[0] + (tmp35 / tmp8) * relativePoint[1] + 1
        return np.array([hy / hw, hx / hw])

    def _rotate90(self,w, d):
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
                if ((w & (1 << b))) != 0:
                    wr |= 1
        return wr

    def _decode(self, tagcode, points):
        """
        decode the tagcode(bin) and calculate distances between code you get and family`s code you own
        :param tagcode: tagcode(binary)
        :param points: quad(four point)
        :return:detection
        """
        tagcode = int(tagcode, 16)  # uncode the code to hex

        bestid = -1
        besthamming = 255
        bestrotation = -1
        bestcode = -1
        rcodes = tagcode

        for r in range(4):
            index = 0
            for tag in self._tagcode:
                dis = bin(tag ^ rcodes).count('1')
                if (dis < besthamming):
                    besthamming = dis
                    bestid = index
                    bestcode = tag
                    bestrotation = r
                index += 1
            rcodes = self._rotate90(rcodes, self._d)
        tagdection = TagDetection()
        tagdection.id = bestid
        tagdection.hammingDistance = besthamming
        tagdection.obsCode = tagcode
        tagdection.matchCode = bestcode
        tagdection.rotation = bestrotation
        if besthamming <= self._hammingdis:
            tagdection.good = True
            tagdection.addPoint(points)
        return tagdection

    def decodeQuad(self, quads, gray):
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
            dd = 2 * self._blackBorder + self._d  # tagFamily.d
            blackvalue = []
            whitevalue = []
            tagcode = 0
            for iy in range(dd):
                for ix in range(dd):
                    x = (ix + 0.5) / dd
                    y = (iy + 0.5) / dd
                    point = np.int32(self._interpolate(quad, (x, y)))
                    points.append(point)
                    value = gray[point[0], point[1]]
                    if ((iy == 0 or iy == dd - 1) or (ix == 0 or ix == dd - 1)):
                        blackvalue.append(value)
                    elif ((iy == 1 or iy == dd - 2) or (ix == 1 or ix == dd - 2)):
                        whitevalue.append(value)
                    else:
                        continue
            threshold = (np.average(blackvalue) + np.average(whitevalue)) / 2
            for iy in range(dd):
                for ix in range(dd):
                    if ((iy == 0 or iy == dd - 1) or (ix == 0 or ix == dd - 1)):
                        continue
                    x = (ix + 0.5) / dd
                    y = (iy + 0.5) / dd
                    point = np.int32(self._interpolate(quad, (x, y)))
                    value = gray[point[0], point[1]]
                    tagcode = tagcode << 1
                    if value > threshold:
                        if(self._debug):
                            whitepoint.append(point)
                        tagcode |= 1
            tagcode = hex(tagcode)
            detection = self._decode(tagcode, quad)
            if detection.good == True:
                detection.addHomography()
                detections.append(detection)
        if self._debug and len(points)!=0:
            plt.figure().set_size_inches(19.2, 10.8)
            plt.subplot(121)
            showpoint = np.array(points)
            plt.plot(showpoint[:, 1], showpoint[:, 0], 'rx')
            plt.imshow(gray)
            plt.gray()
            showpoint = np.array(whitepoint)
            plt.subplot(122)
            plt.plot(showpoint[:, 1], showpoint[:, 0], 'rx')
            plt.imshow(gray)
            plt.gray()
            plt.show()
        return detections

class Tag36h11class(Tagclass):
    def __init__(self,hammingdis = 3,debug = False):
        super().__init__(GLOBAL_TAG36H11,6,debug,hammingdis)
class Tag16h5class(Tagclass):
    def __init__(self,hammingdis = 2,debug = False):
        super().__init__(GLOBAL_TAG25H9, 4, debug, hammingdis)
class Tag25h9class(Tagclass):
    def __init__(self,hammingdis = 2,debug = False):
        super().__init__(GLOBAL_TAG25H9, 5, debug, hammingdis)

GLOBAL_TAG36H11 =  [
0x0000000d5d628584,
0x0000000d97f18b49,
    0x0000000dd280910e,
    0x0000000e479e9c98,
    0x0000000ebcbca822,
    0x0000000f31dab3ac,
    0x0000000056a5d085,
    0x000000010652e1d4,
    0x000000022b1dfead,
    0x0000000265ad0472,
  0x000000034fe91b86,
  0x00000003ff962cd5,
  0x000000043a25329a,
  0x0000000474b4385f,
  0x00000004e9d243e9,
  0x00000005246149ae,
  0x00000005997f5538,
  0x0000000683bb6c4c,
  0x00000006be4a7211,
  0x00000007e3158eea,
  0x000000081da494af,
  0x0000000858339a74,
  0x00000008cd51a5fe,
  0x00000009f21cc2d7,
  0x0000000a2cabc89c,
  0x0000000adc58d9eb,
  0x0000000b16e7dfb0,
  0x0000000b8c05eb3a,
  0x0000000d25ef139d,
  0x0000000d607e1962,
  0x0000000e4aba3076,
  0x00000002dde6a3da,
  0x000000043d40c678,
  0x00000005620be351,
  0x000000064c47fa65,
  0x0000000686d7002a,
  0x00000006c16605ef,
  0x00000006fbf50bb4,
  0x00000008d06d39dc,
  0x00000009f53856b5,
  0x0000000adf746dc9,
  0x0000000bc9b084dd,
  0x0000000d290aa77b,
  0x0000000d9e28b305,
  0x0000000e4dd5c454,
  0x0000000fad2fe6f2,
  0x0000000181a8151a,
  0x000000026be42c2e,
  0x00000002e10237b8,
  0x0000000405cd5491,
  0x00000007742eab1c,
  0x000000085e6ac230,
  0x00000008d388cdba,
  0x00000009f853ea93,
  0x0000000c41ea2445,
  0x0000000cf1973594,
  0x000000014a34a333,
  0x000000031eacd15b,
  0x00000006c79d2dab,
  0x000000073cbb3935,
  0x000000089c155bd3,
  0x00000008d6a46198,
  0x000000091133675d,
  0x0000000a708d89fb,
  0x0000000ae5ab9585,
  0x0000000b9558a6d4,
  0x0000000b98743ab2,
  0x0000000d6cec68da,
  0x00000001506bcaef,
  0x00000004becd217a,
  0x00000004f95c273f,
  0x0000000658b649dd,
  0x0000000a76c4b1b7,
  0x0000000ecf621f56,
  0x00000001c8a56a57,
  0x00000003628e92ba,
  0x000000053706c0e2,
  0x00000005e6b3d231,
  0x00000007809cfa94,
  0x0000000e97eead6f,
  0x00000005af40604a,
  0x00000007492988ad,
  0x0000000ed5994712,
  0x00000005eceaf9ed,
  0x00000007c1632815,
  0x0000000c1a0095b4,
  0x0000000e9e25d52b,
  0x00000003a6705419,
  0x0000000a8333012f,
  0x00000004ce5704d0,
  0x0000000508e60a95,
  0x0000000877476120,
  0x0000000a864e950d,
  0x0000000ea45cfce7,
  0x000000019da047e8,
  0x000000024d4d5937,
  0x00000006e079cc9b,
  0x000000099f2e11d7,
  0x000000033aa50429,
  0x0000000499ff26c7,
   0x000000050f1d3251,
   0x000000066e7754ef,
   0x000000096ad633ce,
   0x00000009a5653993,
   0x0000000aca30566c,
   0x0000000c298a790a,
   0x00000008be44b65d,
   0x0000000dc68f354b,
   0x000000016f7f919b,
   0x00000004dde0e826,
   0x0000000d548cbd9f,
   0x0000000e0439ceee,
   0x0000000fd8b1fd16,
   0x000000076521bb7b,
   0x0000000d92375742,
   0x0000000cab16d40c,
   0x0000000730c9dd72,
   0x0000000ad9ba39c2,
   0x0000000b14493f87,
   0x000000052b15651f,
   0x0000000185409cad,
   0x000000077ae2c68d,
   0x000000094f5af4b5,
   0x00000000a13bad55,
   0x000000061ea437cd,
   0x0000000a022399e2,
   0x0000000203b163d1,
   0x00000007bba8f40e,
   0x000000095bc9442d,
   0x000000041c0b5358,
   0x00000008e9c6cc81,
   0x00000000eb549670,
   0x00000009da3a0b51,
   0x0000000d832a67a1,
   0x0000000dcd4350bc,
   0x00000004aa05fdd2,
   0x000000060c7bb44e,
   0x00000004b358b96c,
   0x0000000067299b45,
   0x0000000b9c89b5fa,
   0x00000006975acaea,
   0x000000062b8f7afa,
   0x000000033567c3d7,
   0x0000000bac139950,
   0x0000000a5927c62a,
   0x00000005c916e6a4,
   0x0000000260ecb7d5,
   0x000000029b7bbd9a,
   0x0000000903205f26,
   0x0000000ae72270a4,
   0x00000003d2ec51a7,
   0x000000082ea55324,
   0x000000011a6f3427,
   0x00000001ca1c4576,
   0x0000000a40c81aef,
   0x0000000bddccd730,
   0x00000000e617561e,
   0x0000000969317b0f,
   0x000000067f781364,
   0x0000000610912f96,
   0x0000000b2549fdfc,
   0x000000006e5aaa6b,
   0x0000000b6c475339,
   0x0000000c56836a4d,
   0x0000000844e351eb,
   0x00000004647f83b4,
   0x00000000908a04f5,
   0x00000007f51034c9,
   0x0000000aee537fca,
   0x00000005e92494ba,
   0x0000000d445808f4,
   0x000000028d68b563,
   0x000000004d25374b,
   0x00000002bc065f65,
   0x000000096dc3ea0c,
   0x00000004b2ade817,
   0x000000007c3fd502,
   0x0000000e768b5caf,
   0x000000017605cf6c,
   0x0000000182741ee4,
  0x000000062846097c,
  0x000000072b5ebf80,
  0x0000000263da6e13,
  0x0000000fa841bcb5,
  0x00000007e45e8c69,
  0x0000000653c81fa0,
  0x00000007443b5e70,
  0x00000000a5234afd,
  0x000000074756f24e,
  0x0000000157ebf02a,
   0x000000082ef46939,
   0x000000080d420264,
   0x00000002aeed3e98,
   0x0000000b0a1dd4f8,
   0x0000000b5436be13,
   0x00000007b7b4b13b,
   0x00000001ce80d6d3,
   0x000000016c08427d,
   0x0000000ee54462dd,
   0x00000001f7644cce,
   0x00000009c7b5cc92,
   0x0000000e369138f8,
   0x00000005d5a66e91,
   0x0000000485d62f49,
   0x0000000e6e819e94,
   0x0000000b1f340eb5,
   0x000000009d198ce2,
   0x0000000d60717437,
   0x00000000196b856c,
   0x0000000f0a6173a5,
   0x000000012c0e1ec6,
   0x000000062b82d5cf,
   0x0000000ad154c067,
   0x0000000ce3778832,
   0x00000006b0a7b864,
   0x00000004c7686694,
   0x00000005058ff3ec,
   0x0000000d5e21ea23,
   0x00000009ff4a76ee,
   0x00000009dd981019,
   0x00000001bad4d30a,
   0x0000000c601896d1,
   0x0000000973439b48,
   0x00000001ce7431a8,
   0x000000057a8021d6,
   0x0000000f9dba96e6,
   0x000000083a2e4e7c,
   0x00000008ea585380,
   0x0000000af6c0e744,
   0x0000000875b73bab,
   0x0000000da34ca901,
   0x00000002ab9727ef,
   0x0000000d39f21b9a,
   0x00000008a10b742f,
   0x00000005f8952dba,
   0x0000000f8da71ab0,
   0x0000000c25f9df96,
   0x000000006f8a5d94,
   0x0000000e42e63e1a,
   0x0000000b78409d1b,
   0x0000000792229add,
   0x00000005acf8c455,
   0x00000002fc29a9b0,
   0x0000000ea486237b,
   0x0000000b0c9685a0,
   0x00000001ad748a47,
   0x000000003b4712d5,
   0x0000000f29216d30,
   0x00000008dad65e49,
   0x00000000a2cf09dd,
   0x00000000b5f174c6,
   0x0000000e54f57743,
   0x0000000b9cf54d78,
   0x00000004a312a88a,
   0x000000027babc962,
   0x0000000b86897111,
   0x0000000f2ff6c116,
   0x000000082274bd8a,
   0x000000097023505e,
   0x000000052d46edd1,
   0x0000000585c1f538,
   0x0000000bddd00e43,
   0x00000005590b74df,
   0x0000000729404a1f,
   0x000000065320855e,
   0x0000000d3d4b6956,
   0x00000007ae374f14,
   0x00000002d7a60e06,
   0x0000000315cd9b5e,
   0x0000000fd36b4eac,
   0x0000000f1df7642b,
   0x000000055db27726,
   0x00000008f15ebc19,
   0x0000000992f8c531,
   0x000000062dea2a40,
   0x0000000928275cab,
   0x000000069c263cb9,
   0x0000000a774cca9e,
   0x0000000266b2110e,
   0x00000001b14acbb8,
  0x0000000624b8a71b,
  0x00000001c539406b,
  0x00000003086d529b,
  0x00000000111dd66e,
  0x000000098cd630bf,
  0x00000008b9d1ffdc,
  0x000000072b2f61e7,
  0x00000009ed9d672b,
  0x000000096cdd15f3,
  0x00000006366c2504,
   0x00000006ca9df73a,
   0x0000000a066d60f0,
   0x0000000e7a4b8add,
   0x00000008264647ef,
   0x0000000aa195bf81,
   0x00000009a3db8244,
   0x0000000014d2df6a,
   0x00000000b63265b7,
   0x00000002f010de73,
   0x000000097e774986,
   0x0000000248affc29,
   0x0000000fb57dcd11,
   0x00000000b1a7e4d9,
   0x00000004bfa2d07d,
   0x000000054e5cdf96,
   0x00000004c15c1c86,
   0x0000000cd9c61166,
   0x0000000499380b2a,
   0x0000000540308d09,
   0x00000008b63fe66f,
   0x0000000c81aeb35e,
   0x000000086fe0bd5c,
   0x0000000ce2480c2a,
   0x00000001ab29ee60,
   0x00000008048daa15,
   0x0000000dbfeb2d39,
   0x0000000567c9858c,
   0x00000002b6edc5bc,
   0x00000002078fca82,
   0x0000000adacc22aa,
   0x0000000b92486f49,
   0x000000051fac5964,
   0x0000000691ee6420,
   0x0000000f63b3e129,
   0x000000039be7e572,
   0x0000000da2ce6c74,
   0x000000020cf17a5c,
   0x0000000ee55f9b6e,
   0x0000000fb8572726,
   0x0000000b2c2de548,
   0x0000000caa9bce92,
   0x0000000ae9182db3,
   0x000000074b6e5bd1,
   0x0000000137b252af,
   0x000000051f686881,
   0x0000000d672f6c02,
   0x0000000654146ce4,
   0x0000000f944bc825,
   0x0000000e8327f809,
   0x000000076a73fd59,
   0x0000000f79da4cb4,
   0x0000000956f8099b,
   0x00000007b5f2655c,
   0x0000000d06b114a6,
   0x0000000d0697ca50,
   0x000000027c390797,
   0x0000000bc61ed9b2,
   0x0000000cc12dd19b,
   0x0000000eb7818d2c,
   0x0000000092fcecda,
   0x000000089ded4ea1,
   0x0000000256a0ba34,
   0x0000000b6948e627,
   0x00000001ef6b1054,
   0x00000008639294a2,
   0x0000000eda3780a4,
   0x000000039ee2af1d,
   0x0000000cd257edc5,
   0x00000002d9d6bc22,
   0x0000000121d3b47d,
   0x000000037e23f8ad,
   0x0000000119f31cf6,
   0x00000002c97f4f09,
   0x0000000d502abfe0,
   0x000000010bc3ca77,
   0x000000053d7190ef,
   0x000000090c3e62a6,
   0x00000007e9ebf675,
   0x0000000979ce23d1,
   0x000000027f0c98e9,
   0x0000000eafb4ae59,
   0x00000007ca7fe2bd,
   0x00000001490ca8f6,
   0x00000009123387ba,
   0x0000000b3bc73888,
   0x00000003ea87e325,
   0x00000004888964aa,
   0x0000000a0188a6b9,
   0x0000000cd383c666,
   0x000000040029a3fd,
  0x0000000e1c00ac5c,
  0x000000039e6f2b6e,
  0x0000000de664f622,
  0x0000000e979a75e8,
  0x00000007c6b4c86c,
  0x0000000fd492e071,
  0x00000008fbb35118,
  0x000000040b4a09b7,
  0x0000000af80bd6da,
  0x000000070e0b2521,
   0x00000002f5c54d93,
   0x00000003f4a118d5,
   0x000000009c1897b9,
   0x0000000079776eac,
   0x0000000084b00b17,
   0x00000003a95ad90e,
   0x000000028c544095,
   0x000000039d457c05,
   0x00000007a3791a78,
   0x0000000bb770e22e,
   0x00000009a822bd6c,
   0x000000068a4b1fed,
   0x0000000a5fd27b3b,
   0x00000000c3995b79,
   0x0000000d1519dff1,
   0x00000008e7eee359,
   0x0000000cd3ca50b1,
   0x0000000b73b8b793,
   0x000000057aca1c43,
   0x0000000ec2655277,
   0x0000000785a2c1b3,
   0x000000075a07985a,
   0x0000000a4b01eb69,
   0x0000000a18a11347,
   0x0000000db1f28ca3,
   0x0000000877ec3e25,
   0x000000031f6341b8,
   0x00000001363a3a4c,
   0x0000000075d8b9ba,
   0x00000007ae0792a9,
   0x0000000a83a21651,
   0x00000007f08f9fb5,
   0x00000000d0cf73a9,
   0x0000000b04dcc98e,
   0x0000000f65c7b0f8,
   0x000000065ddaf69a,
   0x00000002cf9b86b3,
   0x000000014cb51e25,
   0x0000000f48027b5b,
   0x00000000ec26ea8b,
   0x000000044bafd45c,
   0x0000000b12c7c0c4,
   0x0000000959fd9d82,
   0x0000000c77c9725a,
   0x000000048a22d462,
   0x00000008398e8072,
   0x0000000ec89b05ce,
   0x0000000bb682d4c9,
   0x0000000e5a86d2ff,
   0x0000000358f01134,
   0x00000008556ddcf6,
   0x000000067584b6e2,
   0x000000011609439f,
   0x000000008488816e,
   0x0000000aaf1a2c46,
   0x0000000f879898cf,
   0x00000008bbe5e2f7,
   0x0000000101eee363,
   0x0000000690f69377,
   0x0000000f5bd93cd9,
   0x0000000cea4c2bf6,
   0x00000009550be706,
   0x00000002c5b38a60,
   0x0000000e72033547,
   0x00000004458b0629,
   0x0000000ee8d9ed41,
   0x0000000d2f918d72,
   0x000000078dc39fd3,
   0x00000008212636f6,
   0x00000007450a72a7,
   0x0000000c4f0cf4c6,
   0x0000000367bcddcd,
   0x0000000c1caf8cc6,
   0x0000000a7f5b853d,
   0x00000009d536818b,
   0x0000000535e021b0,
   0x0000000a7eb8729e,
   0x0000000422a67b49,
   0x0000000929e928a6,
   0x000000048e8aefcc,
   0x0000000a9897393c,
   0x00000005eb81d37e,
   0x00000001e80287b7,
   0x000000034770d903,
   0x00000002eef86728,
   0x000000059266ccb6,
   0x00000000110bba61,
   0x00000001dfd284ef,
   0x0000000447439d1b,
   0x0000000fece0e599,
  0x00000009309f3703,
  0x000000080764d1dd,
  0x0000000353f1e6a0,
  0x00000002c1c12dcc,
  0x0000000c1d21b9d7,
  0x0000000457ee453e,
  0x0000000d66faf540,
  0x000000044831e652,
  0x0000000cfd49a848,
  0x00000009312d4133,
   0x00000003f097d3ee,
  0x00000008c9ebef7a,
  0x0000000a99e29e88,
   0x00000000e9fab22c,
  0x00000004e748f4fb,
  0x0000000ecdee4288,
   0x0000000abce5f1d0,
   0x0000000c42f6876c,
   0x00000007ed402ea0,
   0x0000000e5c4242c3,
   0x0000000d5b2c31ae,
   0x0000000286863be6,
   0x0000000160444d94,
   0x00000005f0f5808e,
   0x0000000ae3d44b2a,
   0x00000009f5c5d109,
   0x00000008ad9316d7,
   0x00000003422ba064,
   0x00000002fed11d56,
   0x0000000bea6e3e04,
   0x000000004b029eec,
   0x00000006deed7435,
   0x00000003718ce17c,
   0x000000055857f5e2,
   0x00000002edac7b62,
   0x0000000085d6c512,
   0x0000000d6ca88e0f,
   0x00000002b7e1fc69,
   0x0000000a699d5c1b,
   0x0000000f05ad74de,
   0x00000004cf5fb56d,
   0x00000005725e07e1,
   0x000000072f18a2de,
   0x00000001cec52609,
   0x000000048534243c,
   0x00000002523a4d69,
   0x000000035c1b80d1,
   0x0000000a4d7338a7,
   0x00000000db1af012,
   0x0000000e61a9475d,
   0x000000005df03f91,
   0x000000097ae260bb,
   0x000000032d627fef,
   0x0000000b640f73c2,
   0x000000045a1ac9c6,
   0x00000006a2202de1,
   0x000000057d3e25f2,
   0x00000005aa9f986e,
   0x00000000cc859d8a,
   0x0000000e3ec6cca8,
   0x000000054e95e1ae,
   0x0000000446887b06,
   0x00000007516732be,
   0x00000003817ac8f5,
   0x00000003e26d938c,
   0x0000000aa81bc235,
   0x0000000df387ca1b,
   0x00000000f3a3b3f2,
   0x0000000b4bf69677,
   0x0000000ae21868ed,
   0x000000081e1d2d9d,
   0x0000000a0a9ea14c,
   0x00000008eee297a9,
   0x00000004740c0559,
   0x0000000e8b141837,
   0x0000000ac69e0a3d,
   0x00000009ed83a1e1,
   0x00000005edb55ecb,
   0x000000007340fe81,
   0x000000050dfbc6bf,
   0x00000004f583508a,
   0x0000000cb1fb78bc,
   0x00000004025ced2f,
   0x000000039791ebec,
   0x000000053ee388f1,
   0x00000007d6c0bd23,
   0x000000093a995fbe,
   0x00000008a41728de,
   0x00000002fe70e053,
   0x0000000ab3db443a,
   0x00000001364edb05,
   0x000000047b6eeed6,
   0x000000012e71af01,
   0x000000052ff83587,
   0x00000003a1575dd8,
   0x00000003feaa3564,
   0x0000000eacf78ba7,
   0x00000000872b94f8,
   0x0000000da8ddf9a2,
   0x00000009aa920d2b,
  0x00000001f350ed36,
  0x000000018a5e861f,
  0x00000002c35b89c3,
  0x00000003347ac48a,
  0x00000007f23e022e,
  0x00000002459068fb,
  0x0000000e83be4b73
]
GLOBAL_TAG16H5 = [
    0x000000000000231b,
    0x0000000000002ea5,
    0x000000000000346a,
    0x00000000000045b9,
    0x00000000000079a6,
    0x0000000000007f6b,
    0x000000000000b358,
    0x000000000000e745,
    0x000000000000fe59,
    0x000000000000156d,
    0x000000000000380b,
    0x000000000000f0ab,
    0x0000000000000d84,
    0x0000000000004736,
    0x0000000000008c72,
    0x000000000000af10,
    0x000000000000093c,
    0x00000000000093b4,
    0x000000000000a503,
    0x000000000000468f,
    0x000000000000e137,
    0x0000000000005795,
    0x000000000000df42,
    0x0000000000001c1d,
    0x000000000000e9dc,
    0x00000000000073ad,
    0x000000000000ad5f,
    0x000000000000d530,
    0x00000000000007ca,
    0x000000000000af2e
]
GLOBAL_TAG25H9 = [
            0x155cbf1,
            0x1e4d1b6,
            0x17b0b68,
            0x1eac9cd,
            0x12e14ce,
            0x3548bb,
            0x7757e6,
            0x1065dab,
            0x1baa2e7,
            0xdea688,
            0x81d927,
            0x51b241,
            0xdbc8ae,
            0x1e50e19,
            0x15819d2,
            0x16d8282,
            0x163e035,
            0x9d9b81,
            0x173eec4,
            0xae3a09,
            0x5f7c51,
            0x1a137fc,
            0xdc9562,
            0x1802e45,
            0x1c3542c,
            0x870fa4,
            0x914709,
            0x16684f0,
            0xc8f2a5,
            0x833ebb,
            0x59717f,
            0x13cd050,
            0xfa0ad1,
            0x1b763b0,
            0xb991ce
        ]