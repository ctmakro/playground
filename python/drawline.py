
import numpy as np
import cv2
from cv2tools import vis,filt

import random,math

def r(k=1):
    # return random.random()
    return random.gauss(0,k)

def show(*i):
    for j in i:
        vis.show_autoscaled(j,limit=800,)
    cv2.waitKey(0)

canvas = np.zeros((512,512,1), dtype='uint8')+255

# show(canvas)

def line(canvas, x1, y1, x2, y2):
    h,w = canvas.shape[0:2]

    vx = x2-x1
    vy = y2-y1
    dist = math.sqrt(vx**2 + vy**2)

    npoints = int(dist*.5)
    for i in range(npoints):
        # rn = r()
        s = (i+.5)/npoints
        x = vx * s + x1 + r(.5)
        y = vy * s + y1 + r(.5)

        if 0<=y<h and 0<=x<w:
            canvas[int(y),int(x)] = 0

# line(canvas, 128,128,384,384)

for i in range(2000):
    line(canvas,
        r(100)+256,
        r(100)+256,
        r(100)+256,
        r(100)+256,
    )

# blurcanvas

def blurcanvas(canvas):
    f = canvas.astype('float32')

    g = 2.2
    ig = 1/g

    f = (f * (1/255)) ** g
    f = cv2.blur(f,(3,3))
    f = cv2.blur(f,(3,3))
    f=np.clip(f,0,1)
    f = f**ig * 255
    f = f.astype('uint8')

    return f


show(canvas, blurcanvas(canvas))
