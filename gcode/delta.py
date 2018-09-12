import math, time
import numpy as np
from scipy.optimize import minimize

# the delta printer class
class delta:
    # this delta printer model is the one used by Marlin and RepRap.
    # it assumes:
    # the rails are parallel to each other;
    # the bed is flat and perpendicular to the rails.

    def __init__(self):
        # delta structual parameters

        # delta rod length
        self.drl = 217
        # delta radius
        self.dr = 98
        # delta printable radius
        self.pr = 65
        # z height
        self.zh = 300

        # probe positioning offsets
        self.po = np.array([0]*2).astype('float32')
        # tower angle offsets
        self.toa = np.array([0]*3).astype('float32')
        # tower endstop offsets
        self.tes = np.array([0]*3).astype('float32')

        # bed tilt, in x and y dir
        self.bed = np.array([0]*2).astype('float32')

    def copy(self):
        import copy
        return copy.deepcopy(self)

    def __str__(self):
        return 'rod: {:.3f}, radius: {:.3f}, height: {:.3f}, probe_offset: X{:.3f} Y{:.3f}, TxTyTz: {:.3f} {:.3f} {:.3f}, ExEyEz: {:.3f} {:.3f} {:.3f}, Bed: X{:.3f} Y{:.3f}'.format(
            self.drl,
            self.dr,
            self.zh,
            self.po[0],self.po[1],
            self.toa[0],self.toa[1],self.toa[2],
            self.tes[0],self.tes[1],self.tes[2],
            self.bed[0],self.bed[1]
        )

    # output tower 2d coords
    def tower_2d_coords(self):
        # the offsetted angles where the towers are placed at.
        standard_tower_angles = np.array([90+120, 90+240, 90]).astype('float32')
        offsetted_tower_angles = standard_tower_angles + self.toa

        offsetted_tower_radians = offsetted_tower_angles / 180 * np.pi

        # the x,y placement of the three towers.
        tower_coords_x = np.cos(offsetted_tower_radians) * self.dr
        tower_coords_y = np.sin(offsetted_tower_radians) * self.dr

        return tower_coords_x,tower_coords_y

    # foward kinematics
    def fk(self, xyz):
        # xyz[3] are the distances each slider have travelled down along the rails from top endswitch.

        # z height of all the sliders.
        actual_sliders_traveldown_distance = xyz + self.tes
        actual_sliders_height = self.zh - actual_sliders_traveldown_distance

        tower_coords_x, tower_coords_y = self.tower_2d_coords()

        # now the cartesian coordinates of all three sliders are found.
        slider_coords_x = tower_coords_x
        slider_coords_y = tower_coords_y
        slider_coords_z = actual_sliders_height

        sliders = [np.array([
            slider_coords_x[i], slider_coords_y[i], slider_coords_z[i]
        ]) for i in [0,1,2]]

        def trilaterate1(sliders):
            from trilaterate_iterative import trilaterate as trl
            a = trl(sliders, np.array([self.drl]*3))
            return a

        def trilaterate2(sliders):
            from trilaterate import trilaterate as trl
            a,b = trl(sliders, np.array([self.drl]*3))
            return a if a[2]<b[2] else b

        t = trilaterate2(sliders)
        return t

    # inverse kinematics
    def ik(self,xyz):
        # xyz[3] is the point we're trying to reach.

        # 1. calc distance to the rails
        # 2. overheight = sqrt(self.drl**2 - dist**2)
        # 3. actualheight = overheight + point[z]

        tower_coords_x, tower_coords_y = self.tower_2d_coords()

        totalheights = []
        for i in [0,1,2]:
            sqrdist2tower = (xyz[0] - tower_coords_x[i])**2 + (xyz[1] - tower_coords_y[i])**2
            overheight = np.sqrt(self.drl**2 - sqrdist2tower)
            totalheight = overheight + xyz[2]
            totalheights.append(totalheight)

        # the height sliders needed to reach.
        needed_height = np.array(totalheights).astype('float32')

        slider_traveldown_distance = self.zh - needed_height - self.tes
        return slider_traveldown_distance

    # move carriage to x,y and probe downward to bed. returns the point we should hit.
    def probe_at(self, xy):
        offsetted_xy = xy + self.po[0:2] # add probe offset to xy
        # offsetted_xy = xy

        # if self.bed.x > 0 then bed raises toward x+
        bed_z_offset = np.sum(offsetted_xy * self.bed)

        # if bed is perfectly perpendicular, offsets should be zero.
        p = np.array([xy[0], xy[1], bed_z_offset])
        return p

# connect to delta printer and collect data about it.
# Marlin 1.1.4 firmware assumed.
# must support EEPROM.
from parse import *

def collect_delta_data():
    from serial_conn import readfile, run_gcode_collect_lines
    from prob_proc import eatlines

    gcode = readfile('proby.gcode')
    gcode = 'M501\n' + gcode

    lines = run_gcode_collect_lines(gcode)
    # array

    print('collected:')
    for l in lines:
        print(l)

    # extract bed_probing_result
    bed_probing_result = list(filter(lambda x:x[0:3]=='Bed', lines))
    idx = 0
    def feed():
        nonlocal idx
        if idx<len(bed_probing_result):
            l = bed_probing_result[idx]; idx+=1
            return l
        else:
            return ''
    xs,ys,zs = eatlines(feed)

    # extract M666 setting
    m666 = list(filter(lambda x:x[0:11]=='echo:  M666', lines))[0]
    m666 = parse("echo:  M666 X{:f} Y{:f} Z{:f}", m666).fixed

    # extract M665 setting
    m665 = list(filter(lambda x:x[0:11]=='echo:  M665', lines))[0]
    m665 = parse("echo:  M665 L{:f} R{:f} H{:f} S{:f} B{:f} X{:f} Y{:f} Z{:f}", m665).fixed

    probe_points = [[xs[i],ys[i],zs[i]] for i in range(len(xs))]
    data = {
        'points':probe_points,
        'endstops':list(m666),
        'tower_angle_offsets':list(m665[5:8]),
        'z_height':m665[2],
        'radius':m665[1],
        'rod_length':m665[0],
        'probe_radius':m665[4],
    }
    return data

def collect_and_save():
    import json
    global data,ppd
    data = collect_delta_data()
    zs = [p[2] for p in data['points']]
    ppd = max(zs) - min(zs)
    jayson = json.dumps(data)
    with open('data.json','w') as f:
        f.write(jayson)
        print('data written to data.json')

def plotsurf():
    global data
    dp = data['points']
    from prob_proc import plotsurf
    plotsurf([[dp[i][k] for i in range(len(dp))] for k in [0,1,2]])

def solve():
    # load from file
    import json
    with open('data.json','r') as f:
        data = json.loads(f.read())
        print('data read from data.json')
    # print(data)

    points = data['points']
    endstops = data['endstops']
    tower_angle_offsets = data['tower_angle_offsets']
    z_height = data['z_height']
    radius = data['radius']
    rod_length = data['rod_length']

    # 1. create the ideal printer
    global ideal
    ideal = delta()
    ideal.drl = rod_length
    ideal.dr = radius
    ideal.zh = z_height
    ideal.toa = np.array(tower_angle_offsets)
    ideal.tes = np.array(endstops)

    print('ideal printer:')
    print(ideal)
    print('number of points collected:',len(points))

    # serialize printer's parameter into 1-d np array
    def numpyize(p):
        n = np.array([p.dr,p.zh]+list(p.toa[0:3])+list(p.tes))
        assert len(n) == 8
        return n

    # deserialize
    def printerize(n):
        assert len(n) == 8
        p = ideal.copy()
        # p.drl = n[0]
        p.dr = n[0]
        p.zh = n[1]
        p.toa[0:3] = n[2:5]
        p.tes[0:3] = n[5:8]
        # p.bed[0:2] = n[8:10]
        # p.po[0:2] = n[10:12]
        p.po[0] = 15
        p.po[1] = -15
        return p

    # 2. initial guess
    x0 = numpyize(ideal)

    # 3. create the optimizable function
    def error(n):
        actual = printerize(n)
        hits = []
        total_error = 0
        for p in points:
            probe_point = np.array(p)
            # probe_point[0:2] += actual.po # add offset to it

            # how far did the ideal printer's slider travel, given probe point?
            travels = ideal.ik(probe_point)

            # where will the actual printer result in, given the travel distances?
            hit = actual.fk(travels)
            hits.append(hit)

        for h in hits:
            # if the actual printer probe at the hit(x,y) position, what Z should we reach?
            z = actual.probe_at(h[0:2])[2]

            # what's the difference between the Z we should reach, and the Z actually reached?
            diff = (z-h[2])**2
            total_error += diff

        return total_error

    # 4. optimize!
    print('optimizing...')
    res = minimize(error, x0, method='nelder-mead',
        options = {'xatol':3e-5,'fatol':3e-5, 'disp':True}
    )
    # res = minimize(error, x0, method='powell',
    #     options = {'disp':True}
    # )
    actual = printerize(res.x)
    print('estimated actual printer parameters:')
    print(actual)
    global estimated
    estimated = actual

def writeback(idx = -1):
    from serial_conn import readfile, run_gcode_collect_lines
    # global estimated
    global ests

    estimated = ests[idx]
    print('(writeback) ests[]', idx)
    print('attempting to write back to printer...')
    print(estimated)
    # write back only the important parameters

    # tower endstop offsets mustn't be positive
    positive_bias = np.max(estimated.tes)
    estimated.tes -= positive_bias
    estimated.zh -= positive_bias

    # tower offset angles shoud zero on z
    toaz = estimated.toa[2]
    estimated.toa[0:3] -= toaz

    newe = estimated.copy()
    alpha = 1
    newe.tes = newe.tes * alpha + ideal.tes * (1-alpha)
    newe.zh = newe.zh * alpha + ideal.zh * (1-alpha)
    newe.dr = newe.dr * alpha + ideal.dr * (1-alpha)
    newe.toa = newe.toa * alpha + ideal.toa * (1-alpha)

    m665 = 'M665 L{:.3f} R{:.3f} H{:.3f} X{:.3f} Y{:.3f} Z{:.3f}\n'.format(
        estimated.drl, estimated.dr, estimated.zh,
        estimated.toa[0],
        estimated.toa[1],
        estimated.toa[2],
    )

    m666 = 'M666 X{:.3f} Y{:.3f} Z{:.3f}\n'.format(
        estimated.tes[0],
        estimated.tes[1],
        estimated.tes[2],
    )

    newline = '\n'
    total = m665 + newline + m666 + newline + 'M500\nM501\n'

    lines = run_gcode_collect_lines(total)
    print('writeback successful.')

ran = False
ppd = 0
ppds,ests = [],[]

def runonce(iter=3):
    global estimated, ran, ppd, ppds, ests

    if ran == False:
        collect_and_save()
        ran = True

    for i in range(iter):
        # plotsurf()
        solve()
        ests.append(estimated)
        writeback()
        collect_and_save()
        # sds.append(sd)
        ppds.append(ppd)

    for idx,e in enumerate(ests):
        print('Estimate', idx)
        print(e)
        print('p-p Deviation:', ppds[idx])

    plotsurf()

if __name__ == '__main__':
    # main()
    # collect_and_save()
    pass
