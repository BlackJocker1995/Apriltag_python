# Apriltag python


## Apriltag
AprilTag is a visual fiducial system, useful for a wide variety of tasks including augmented reality, robotics, and camera calibration. Targets can be created from an ordinary printer, and the AprilTag detection software computes the precise 3D position, orientation, and identity of the tags relative to the camera. Implementations are available in Java, as well as in C. Notably, the C implementation has no external dependencies and is designed to be easily included in other applications, as well as portable to embedded devices. Real-time performance can be achieved even on cell-phone grade processors.

The two main papers to refer to understand the apriltag algorithm are the following:

1. IROS 2016 - [AprilTag 2: Efficient and robust fiducial detection](https://april.eecs.umich.edu/media/pdfs/wang2016iros.pdf): this is the paper which refers to the version of the algorithm that we want to use

2. ICRA 2011 - [AprilTag: A robust and flexible visual fiducial system](https://ieeexplore.ieee.org/abstract/document/5979561/): this is the paper which explains how the first version of the algorithm works

## Apriltag python
This program is base on apriltag without any c extra plugin.And this program encompass tag36h11 tag25h9 and tag16h5.If you han any idea about enchance this program`s function,you can modify whatever you want.
Just support tag36h11,tag25h9,tag16h5.

## How to use it
1. You should install the opencv and other lib.Your python version must higher that 2.7(not support).
2. Now you can run files starting with test*.py
3. fold named camtest contains some operation about camera and aprilt,but it still not finished.


## Other
This project is my graduation project.So if you want to use or modify this project,please add some information about me. 

Author:rain

E-Mail:raindown95@outlook.com


## 关于Apriltag python
仅支持 tag36h11,tag25h9,tag16h5，如有需要可自行添加。本程序不支持python2.7，有需求用户可以自行更改。

## 如何使用
1. 首先要安装opencv和其他python包。
2. 直接运行任意一个test开头的文件。
3. camtest是一些其他有关摄像头的工作，并没有完全完工。
