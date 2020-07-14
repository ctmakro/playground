import numpy as np

# screen pixels

screenx = 640
screeny = 480

# screen coords of every pixel
x = np.linspace(0,screenx-1,screenx)
# 0 - 639
y = np.linspace(0,screeny-1,screeny)
# 0 - 319

scx, scy = np.meshgrid(x,y)

# print(scx.shape, scy.shape)
# print(scx)
# print(scy)

# ray vectors, starting from origin, pointing to screen pixels. screen pixels are moved to Z=1

rvx = (scx-screenx/2+0.5) / screenx
# mapped to -0.5...0.5
rvy = (scy-screeny/2+0.5) / screenx
# mapped with the same scale as x
rvz = np.ones_like(rvx)

# print(rvy)

from collections import namedtuple as nt
Ball = nt('Ball', 'x,y,z,r')

ball = Ball(0,0,3,1)
# ball located at z=3 with radius 1.

# test whether rays intersect with the ball:

def intersect(vx,vy,vz, ball):
    # calculate distance from ray to ball center.
    # we can rotate the ball center by ray vector,
    # then calculate dist from ball's center to z axis.
