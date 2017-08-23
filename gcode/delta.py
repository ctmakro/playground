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

        # print('ash',actual_sliders_height)
        # for s in sliders:
        #     print('slider cartesian', s)
        def normalized(v):
            norm = np.sqrt(np.sum(v**2))
            return v / norm
        # Trilateration to find the target point, given slider positions
        def trilaterate(sliders):

            # initial guess
            t = np.array([0,0,-10]).astype('float32')
            v = t*0
            for i in range(1000):
                # print('t@',i,t)
                total_force = v*0
                tick = 0
                for slider in sliders:
                    diff = slider - t # direction vector towards sphere center
                    delta_dist = (np.sqrt(np.sum(diff**2)) - self.drl) # distance difference

                    force = delta_dist * normalized(diff)
                    total_force+=force
                    # print('dtdist',delta_dist)

                    if abs(delta_dist) < 1e-2:
                        tick+=1

                if tick>=3:
                    break
                else:
                    tick=0

                v += total_force # dampen-spring simulation
                v *= 0.9
                t += v
            print('(fk) took',i+1,'iteration to solve trilateration')
            return t

        t = trilaterate(sliders)
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
