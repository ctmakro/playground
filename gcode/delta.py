import math, time
import numpy as np

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
        self.po = np.array([0,0,0]).astype('float32')
        # tower angle offsets
        self.toa = np.array([0,0,0]).astype('float32')
        # tower endstop offsets
        self.tes = np.array([0,0,0]).astype('float32')

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

        # def normalized(v):
        #     norm = np.sqrt(np.sum(v**2))
        #     return v / norm
        # # Trilateration to find the target point, given slider positions
        # def trilaterate(sliders):
        #
        #     # initial guess
        #     t = np.array([0,0,-10]).astype('float32')
        #     v = t*0
        #     for i in range(1000):
        #         # print('t@',i,t)
        #         total_force = v*0
        #         tick = 0
        #         for slider in sliders:
        #             diff = slider - t # direction vector towards sphere center
        #             delta_dist = (np.sqrt(np.sum(diff**2)) - self.drl) # distance difference
        #
        #             force = delta_dist * normalized(diff)
        #             total_force+=force
        #             # print('dtdist',delta_dist)
        #
        #             if abs(delta_dist) < 1e-2:
        #                 tick+=1
        #
        #         if tick>=3:
        #             break
        #         else:
        #             tick=0
        #
        #         v += total_force # dampen-spring simulation
        #         v *= 0.9
        #         t += v
        #     print('(fk) took',i+1,'iteration to solve trilateration')
        #     return t

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

def main():
    d = delta()
    d.toa[0] += 1
    d.toa[1] -= .9
    d.tes[0] -= 4.4
    d.tes[1] -= 0.2

    p = np.array([5,8,10])
    print(p)

    sliders = d.ik(p)
    print(sliders)

    p = d.fk(sliders)
    print(p)

if __name__ == '__main__':
    main()

def ttrilaterate(points, distances, return_middle):
    import numpy as np
    p1,p2,p3 = points
    # point -> np arrays in the form of [x, y, z]
    # distances -> np array [r1, r2, r3]
    def norm(v):
        return np.sqrt(np.sum(v**2))
    def dot(v1,v2):
        return np.dot(v1,v2)
    def cross(v1,v2):
        return np.cross(v1,v2)

    ex = (p2-p1) /  norm(p2-p1)
    i = dot(ex,p3-p1)
    a = (p3-p1) - ex*i
    ey = a/norm(a)
    ez = cross(ex,ey)
    d = norm(p2-p1)
    j = dot(ey,p3-p1)
    x = (distances[0]**2 - distances[1]**2 + d**2) / (2*d)
    y = (distances[0]**2 - distances[2]**2 + i**2 + j**2) / (2*j) - (i/j) * x
    b = distances[0]**2 - x**2 - y**2

    z = np.sqrt(b)
    if math.isnan(z):
        raise Exception('NaN met, cannot solve for z')

    a = p1 + ex*x + ey*y
    p4a = a + ez*z
    p4b = a - ez*z

    return p4a, p4b

# 	i = dot(ex, vector_subtract(p3, p1));
# 	a = vector_subtract(vector_subtract(p3, p1), vector_multiply(ex, i));
# 	ey = vector_divide(a, norm(a));
# 	ez =  vector_cross(ex, ey);
# 	d = norm(vector_subtract(p2, p1));
# 	j = dot(ey, vector_subtract(p3, p1));
#
#
# 	x = (sqr(p1.r) - sqr(p2.r) + sqr(d)) / (2 * d);
# 	y = (sqr(p1.r) - sqr(p3.r) + sqr(i) + sqr(j)) / (2 * j) - (i / j) * x;
#
# 	b = sqr(p1.r) - sqr(x) - sqr(y);
#
# 	// floating point math flaw in IEEE 754 standard
# 	// see https://github.com/gheja/trilateration.js/issues/2
# 	if (Math.abs(b) < 0.0000000001)
# 	{
# 		b = 0;
# 	}
#
# 	z = Math.sqrt(b);
#
# 	// no solution found
# 	if (isNaN(z))
# 	{
# 		return null;
# 	}
#
# 	a = vector_add(p1, vector_add(vector_multiply(ex, x), vector_multiply(ey, y)))
# 	p4a = vector_add(a, vector_multiply(ez, z));
# 	p4b = vector_subtract(a, vector_multiply(ez, z));
#
# 	if (z == 0 || return_middle)
# 	{
# 		return a;
# 	}
# 	else
# 	{
# 		return [ p4a, p4b ];
# 	}
# }
