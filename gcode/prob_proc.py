import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors, ticker, cm
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'

import numpy as np

from parse import *

def getlinefromstdin():
    return input('line:')

def getlinefromfile(name):
    f = open(name,'r')
    ls = f.read().split('\n')
    f.close()

    idx = -1
    def get():
        nonlocal ls,idx
        idx+=1
        return ls[idx]

    return get

def eatlines(lineget):
    lines = []
    while True:
        l = lineget()
        if len(l)==0:
            break
        else:
            lines.append(l)

    xs,ys,zs = [],[],[]
    for l in lines:
        fixed = parse("Bed X: {:f} Y: {:f} Z: {:f}",l).fixed
        # print (x,y,z)
        print(fixed)
        x,y,z = fixed
        xs.append(x)
        ys.append(y)
        zs.append(z)

    return xs,ys,zs

def plotsurf(xyztuple):
    xs,ys,zs = xyztuple

    lim = lambda x:min(max(x,0),1)
    cs = [(lim(max(0,z*10)), lim(max(0,-z*10)), 0.2) for z in zs]

    fig = plt.figure()

    ax = fig.add_subplot(121,projection='3d')
    ax.scatter(xs,ys,zs, c=cs, marker='o')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    def grid(x, y, z, resX=32, resY=32):
        from numpy import linspace, meshgrid
        from matplotlib.mlab import griddata

        "Convert 3 column data to matplotlib grid"
        xi = linspace(min(x), max(x), resX)
        yi = linspace(min(y), max(y), resY)
        Z = griddata(x, y, z, xi, yi, interp='linear')
        X, Y = meshgrid(xi, yi)
        return X, Y, Z

    X, Y, Z = grid(xs, ys, zs)
    ax2 = fig.add_subplot(122)
    ax2.contourf(X, Y, Z)

    ax2.plot((-10, 10), (0, 0), 'w-')
    ax2.plot((0, 0), (-10, 10), 'w-') 

    plt.show()

def plotfromfile(filename):
    xyztuple = eatlines(getlinefromfile(filename))
    plotsurf(xyztuple)

if __name__ == '__main__':
    plotfromfile('probing_result.txt')
