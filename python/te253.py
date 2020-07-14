import numpy as np
import cv2

from cv2tools import vis, filt

w = 4096

x = np.linspace(-.5,.5,w)
y = np.linspace(-.5,.5,w)

print(x.shape)
# x = np.meshgrid()
x,y = np.meshgrid(x,y,sparse=False)

rad = np.arctan2(y,x)

nslit = 128
color = np.sin(rad * nslit) *0.5 + 0.5
color = color ** 0.4545
print(color.shape)
vis.show_autoscaled(color)
cv2.waitKey(0)

color = np.clip(color, 0, 1) * 255

cv2.imwrite('out.png', color)
