#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import tagUtils as tud
import numpy as np
from vispy import gloo, app
from vispy.gloo import set_viewport, clear
from vispy.util.transforms import  rotate
import apriltag as ap
import time
vertp = """
#version 120
// Uniforms
// ------------------------------------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;
uniform float u_size;
uniform vec3 u_position;
// Attributes
// ------------------------------------
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_linewidth;
attribute float a_size;
// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;
void main (void) {
    v_size = a_size * u_size;
    v_linewidth = a_linewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = u_projection * u_view * u_model *
        vec4(u_position*u_size,1.0);
    gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
}
"""

vert = """
#version 120
// Uniforms
// ------------------------------------
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
uniform float u_antialias;
uniform float u_size;
// Attributes
// ------------------------------------
attribute vec3  a_position;
attribute vec4  a_fg_color;
attribute vec4  a_bg_color;
attribute float a_linewidth;
attribute float a_size;
// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;
void main (void) {
    v_size = a_size * u_size;
    v_linewidth = a_linewidth;
    v_antialias = u_antialias;
    v_fg_color  = a_fg_color;
    v_bg_color  = a_bg_color;
    gl_Position = u_projection * u_view * u_model *
        vec4(a_position*u_size,1.0);
    gl_PointSize = v_size + 2*(v_linewidth + 1.5*v_antialias);
}
"""

frag = """
#version 120
// Constants
// ------------------------------------
// Varyings
// ------------------------------------
varying vec4 v_fg_color;
varying vec4 v_bg_color;
varying float v_size;
varying float v_linewidth;
varying float v_antialias;
// Functions
// ------------------------------------
float marker(vec2 P, float size);
// Main
// ------------------------------------
void main()
{
    float size = v_size +2*(v_linewidth + 1.5*v_antialias);
    float t = v_linewidth/2.0-v_antialias;
    // The marker function needs to be linked with this shader
    float r = marker(gl_PointCoord, size);
    float d = abs(r) - t;
    if( r > (v_linewidth/2.0+v_antialias))
    {
        discard;
    }
    else if( d < 0.0 )
    {
       gl_FragColor = v_fg_color;
    }
    else
    {
        float alpha = d/v_antialias;
        alpha = exp(-alpha*alpha);
        if (r > 0)
            gl_FragColor = vec4(v_fg_color.rgb, alpha*v_fg_color.a);
        else
            gl_FragColor = mix(v_bg_color, v_fg_color, alpha);
    }
}
float marker(vec2 P, float size)
{
    float r = length((P.xy - vec2(0.5,0.5))*size);
    r -= v_size/2;
    return r;
}
"""

vs = """
uniform mat4 u_model;
attribute vec3 a_position;
attribute vec4 a_fg_color;
attribute vec4 a_bg_color;
attribute float a_size;
attribute float a_linewidth;
void main(){
    gl_Position = u_model *vec4(a_position, 1.);
}
"""

fs = """
void main(){
    gl_FragColor = vec4(0., 0., 0., 1.);
}
"""


zoom = 0.0008
class Canvas(app.Canvas):

    def __init__(self, **kwargs):
        # Initialize the canvas for real
        app.Canvas.__init__(self, keys='interactive', size=(960, 960),
                            **kwargs)
        ps = self.pixel_scale
        #######################################
        n = 8
        data = np.zeros(n, dtype=[('a_position', np.float32, 3),
                                  ('a_fg_color', np.float32, 4),
                                  ('a_bg_color', np.float32, 4),
                                  ('a_size', np.float32, 1),
                                  ('a_linewidth', np.float32, 1),
                                  ])
        edges = np.array([[0, 1], [1, 2], [2, 3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]], dtype='uint32')
        data['a_position'] = zoom*np.array([[0,0,0],[1000,0,0],[1000,1000,0],[0,1000,0],[0,0,1000],[1000,0,1000],[1000,1000,1000],[0,1000,1000]])
        data['a_fg_color'] = 0, 0, 0, 1
        color = np.random.uniform(0.5, 1., (n, 3))
        data['a_bg_color'] = np.hstack((color, np.ones((n, 1))))
        data['a_size'] = 12*np.ones(n)
        data['a_linewidth'] = 1.*ps
        u_antialias = 1

        self.translate = 5
        self.vbo = gloo.VertexBuffer(data)

        self.theta = 0
        self.phi = 0
        self.index = gloo.IndexBuffer(edges)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))
        self.projection = np.eye(4, dtype=np.float32)

        self.program = gloo.Program(vert, frag)
        self.program.bind(self.vbo)
        self.program['u_size'] = 1
        self.program['u_antialias'] = u_antialias
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        self.program['u_projection'] = self.projection
        ###########################################
        m=2
        data1 = np.zeros(m, dtype=[
                                  ('a_fg_color', np.float32, 4),
                                  ('a_bg_color', np.float32, 4),
                                  ('a_size', np.float32, 1),
                                  ('a_linewidth', np.float32, 1),
                                  ])
        data1['a_fg_color'] = 0, 0, 0, 1
        color1 = np.random.uniform(0.5, 1., (m, 3))
        data1['a_bg_color'] = np.hstack((color1, np.ones((m, 1))))
        data1['a_size'] = np.random.randint(size=m, low=8 * ps, high=20 * ps)
        data1['a_linewidth'] = 1. * ps


        self.program_e = gloo.Program(vs, fs)
        self.program_e.bind(self.vbo)
        self.program_e['u_model'] = self.model


        ############################################################
        self.vbo1 = gloo.VertexBuffer(data1)
        self.program_p = gloo.Program(vertp, frag)
        self.program_p.bind(self.vbo1)
        self.program_p['u_position'] = zoom * np.array([[0, 0, 0]])
        self.program_p['u_size'] = 1
        self.program_p['u_antialias'] = u_antialias
        self.program_p['u_model'] = self.model
        self.program_p['u_view'] = self.view
        self.program_p['u_projection'] = self.projection
        self.num = 1
        ############################################################
        set_viewport(0, 0, *self.physical_size)
        gloo.set_state('translucent', clear_color='white')
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        ##############################################################
        self.apriltag = ap.Apriltag()
        self.apriltag.create_detector(thresholding='adaptive',debug=False)
        self.imageImdex = 0
        self.imagenum = 5
        self.frames = []
        self.init_image()
        ##############################################################
        self.show()
    def on_mouse_wheel(self, event):
        pass
        #self.rotate_graph()

    def on_mouse_move(self,event):
       pass


    def on_mouse_press(self, event):
       pass
    def on_mouse_release(self,event):
        pass
    def on_resize(self, event):
        set_viewport(0, 0, *event.physical_size)

    def on_timer(self, event):
        #self.rotate_graph()
        pass
    def on_key_press(self, event):

        if event.text == 'w':
            self.phi += 2
            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))
        if event.text == 's':
            self.phi -= 2
            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))
        if event.text == 'a':
            self.theta += 2
            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))
        if event.text == 'd':
            self.theta -= 2
            self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                                rotate(self.phi, (0, 1, 0)))

        if event.text =='i':
            self.change_point()
        if event.text == ' ':
            if self.timer.running:
                self.timer.stop()
            else:
                self.timer.start()
        self.program['u_model'] = self.model
        self.program_e['u_model'] = self.model
        self.program_p['u_model'] = self.model
        self.update()

    def on_draw(self, event):
        clear(color=True, depth=True)
        self.program_e.draw('lines', self.index)
        self.program.draw('points')
        self.program_p.draw('points')

    def init_image(self):
        strname = '../3dpicture7'
        for index in range(0, self.imagenum):
            filename = strname + '/0_' + str(index) + '.jpg'
            filename1 = strname + '/1_' + str(index) + '.jpg'
            filename2 = strname + '/2_' + str(index) + '.jpg'
            filename3 = strname + '/3_' + str(index) + '.jpg'
            frame = cv2.imread(filename)
            frame1 = cv2.imread(filename1)
            frame2 = cv2.imread(filename2)
            frame3 = cv2.imread(filename3)
            self.frames.append(np.array([frame,frame1,frame2,frame3]))


    def detector_im(self):
        frametmp = self.frames[self.imageImdex]
        detections = self.apriltag.detect(frametmp[3])
        detections1 = self.apriltag.detect(frametmp[2])
        detections2 = self.apriltag.detect(frametmp[1])
        detections3 = self.apriltag.detect(frametmp[0])
        if (len(detections)<1 or len(detections1)<1 or len(detections2)<1 or len(detections3)<1):
            return np.array([0,0,0,0])
        tmp = 121938.0923
        add = 0

        dis = tud.get_min_distance(detections, tmp) + add
        dis1 = tud.get_min_distance(detections1, tmp) + add
        dis2 = tud.get_min_distance(detections2, tmp) + add
        dis3 = tud.get_min_distance(detections3, tmp) + add
        dege = 1050
        x, y, z = tud.sovle_coord(dis, dis1, dis3, dege)
        x2, y2, z2 = tud.sovle_coord(dis2, dis3, dis1, dege)

        nz = tud.verify_z(x, y, dis2, dege)
        nz2 = tud.verify_z(x2, y2, dis, dege)

        x2, y2, nz2 = [dege - x2, dege - y2, nz2]

        point = np.array([x, y, nz,z])
        point2 = np.array([x2, y2, nz2,z2])

        print(point)
        print(point2)
        print((point + point2 ) / 2)
        print()
        return (point + point2 ) / 2

    def rotate_graph(self):
        self.theta += 2
        self.phi += 2
        self.model = np.dot(rotate(self.theta, (0, 0, 1)),
                            rotate(self.phi, (0, 1, 0)))
        self.program['u_model'] = self.model
        self.program_e['u_model'] = self.model
        self.program_p['u_model'] = self.model
        self.update()

    def change_point(self):
        if self.imageImdex < self.imagenum:
            t0 = time.clock()
            x,y,z,t= self.detector_im()
            print(time.clock() - t0)
            self.program_p['u_position'] =zoom*np.array([x,y,z])
            self.imageImdex = self.imageImdex+1
            self.update()
        else:
            print('no more picture')
