# G1 X-28.281 Y24.434 E253.17303
# G1 X-28.284 Y24.433 E253.17317
# G1 X-28.423 Y24.378 E253.17938
# G1 X-28.461 Y24.363 E253.18108
# G1 X-28.504 Y24.346 E253.183

from math import *

xt =-28.504 - -28.461
yt = 24.346 - 24.363
et = 253.183 - 253.18108

sumt = sqrt(xt**2 + yt**2)

extbuffer = 0
def extrude_length(dist):
    global extbuffer
    delta_e = dist  / sumt * et
    extbuffer+= delta_e
    return extbuffer

outbuffer = ''

def code(c):
    global outbuffer
    outbuffer += c + '\n'; print(c)

globalx,globaly = 0,0

def at(x,y):
    global globalx,globaly
    globalx = x;globaly=y

def goto(x,y,extrude=True):
    global globalx,globaly
    dist = sqrt((x-globalx)**2 + (y-globaly)**2) if extrude else 0
    at(x,y)
    e = extrude_length(dist)
    # code('G1 X'+str(x)+' Y'+str(y)+' E'+str(e))
    code('G1 X{:.4} Y{:.4} E{:.4}'.format(x,y,e))

def goto2(x,y,extrude=True):
    return goto(y,x,extrude)

def save(name):
    global outbuffer
    with open(name+'.gcode','w') as f:
        f.write(outbuffer)


def main():
    code('G92 E0')
    code('G1 E3')
    code('G92 E0')


    code('M106 S255')
    code('G28')

    code('G1 F5000 X0 Y0 Z5')
    code('G1 F900 X0 Y0 Z0.4 E0')


    scale = 100

    rows = 10
    step = scale/rows
    hs = step/4

    okflag = True

    for row in range(rows):
        yoff = -scale/2 + row*step
        goto(-scale/2-hs,yoff,extrude=not okflag)
        goto(scale/2-hs,yoff)
        goto(scale/2-hs,yoff+step/2)
        goto(-scale/2-hs,yoff+step/2)

        if okflag==True:
            okflag=False

    okflag = True

    for row in range(rows):
        yoff = -scale/2 + row*step
        goto2(-scale/2-hs,yoff,extrude=not okflag)
        goto2(scale/2-hs,yoff)
        goto2(scale/2-hs,yoff+step/2)
        goto2(-scale/2-hs,yoff+step/2)

        if okflag==True:
            okflag=False

    code('G28')

    save('gridy')
# main()

def main2():
    code('G33P5')
    code('G28')
    code('G90')

    code('G1 F5000 X0 Y0 Z100')
    import random
    def r(n):
        return random.random()*n

    # step1: mesh grid points

    ps = []
    for x in range(-50,51,20):
        for y in range(-50,51,20):
            ps.append((x,y))

    # step2: sort by distance, find closest

    import math
    def dist(p1,p2):
        return math.sqrt(sum([(p1[k]-p2[k])**2 for k in [0,1]]))

    def closest(p,l):
        mindist = 9999
        index = -1
        for i in range(len(l)):
            d = dist(l[i],p)
            if d<mindist:
                mindist = d
                index = i
        return index

    sp = []
    sp.append(ps[0])
    del ps[0]

    while len(ps)>0:
        last = sp[-1]
        nidx = closest(last,ps)
        sp.append(ps[nidx])
        del ps[nidx]

    for x,y in sp:
        code('G1 X{} Y{}'.format(x,y))
        code('G30') # probe

    save('proby')

main2()
