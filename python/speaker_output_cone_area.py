nzone=4

r = 1

import math
import numpy as np

def circlearea(r):
    return math.pi*r*r

def r2area(start,end):
    return circlearea(end)-circlearea(start)

taps =[i/nzone for i in range(nzone+1)]

print(taps)

def a(taps, f):
    nzone = len(taps)-1

    rs = [f(taps[i],taps[i+1]) for i in range(nzone)]

    rs = np.array(rs)

    # avg = np.mean(rs)

    avg = np.arange(nzone+1)
    avg = avg/nzone
    avg = avg**2
    # print(avg)
    avg = avg[1:]-avg[:-1]
    avg[0]=avg[0]/1.414
    avg /=avg.mean()

    # print('a',nzone,rs, avg)

    rs /= rs.mean() # reduce sum to 1

    # ns = np.array(rs,dtype='float32')
    std = np.mean((rs - avg)**2)

    return std

def aa(f):
    def k(tap):
        # t2 = taps[1:-1]
        ntaps = [0]+list(tap)+[1]
        return a(ntaps, f)
    return k

from scipy.optimize import minimize

res = minimize(aa(r2area), x0=taps[1:-1], tol=1e-5)
print(res)

print(*['{:.3f}'.format(i) for i in res.x])
print(*['{:.3f}'.format(i*24) for i in res.x])

# optimized taps for circle-ring-area :[.447, .632, .775, .894]

def domearea(a):
    return math.pi*2*r*r*(1-math.cos(a*math.pi/2))

print(domearea(1))

taps =[i/nzone for i in range(nzone+1)]

def d2area(start, end):
    return domearea(end)-domearea(start)

res = minimize(aa(d2area), x0=taps[1:-1], tol=1e-5)
print(res)
print(*['{:.3f}'.format(i) for i in res.x])

k = res.x
k = [i*90 for i in k]
print(*['{:.1f}'.format(i) for i in k])

# optimized taps for sphere-dome-ring-area:0.410 0.590 0.738 0.872
# 36.87 53.13 66.42 78.46
# deg
