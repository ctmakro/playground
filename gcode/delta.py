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

    # foward kinematics
    def fk(self, xyz):
        # xyz[3] are the distances each slider have travelled down along the rails from top endswitch.

        # z height of all the sliders.
        actual_sliders_traveldown_distance = xyz + self.tes
        actual_sliders_height = self.zh - actual_sliders_traveldown_distance

        # the offsetted angles where the towers are placed at.
        standard_tower_angles = np.array([90,210,330]).astype('float32')
        offsetted_tower_angles = standard_tower_angles + self.toa

        # the x,y placement of the three towers.
        tower_coords_x = np.cos(standard_tower_angles) * self.dr
        tower_coords_y = np.sin(standard_tower_angles) * self.dr

        # now the cartesian coordinates of all three sliders are found.
        slider_coords_x = tower_coords_x
        slider_coords_y = tower_coords_y
        slider_coords_z = actual_sliders_height

        sliders = [np.array([
            slider_coords_x[i], slider_coords_y[i], slider_coords_z[i]
        ]) for i in [0,1,2]]

        print('ash',actual_sliders_height)
        for s in sliders:
            print('slider cartesian', s)

        # Trilateration to find the target point, given slider positions
        def trilaterate(sliders):
            def normalized(v):
                norm = np.sqrt(np.sum(v**2))
                return v / norm
            # initial guess
            t = np.array([0,0,-10]).astype('float32')
            v = t*0
            for i in range(1000):
                print('t@',i,t)
                total_force = v*0
                tick = 0
                for slider in sliders:
                    diff = slider - t # direction vector towards sphere center
                    delta_dist = (np.sqrt(np.sum(diff**2)) - self.drl) # distance difference

                    force = delta_dist * normalized(diff)
                    total_force+=force
                    print('dtdist',delta_dist)

                    if abs(delta_dist) < 2e-3:
                        tick+=1

                if tick>=3:
                    return t
                else:
                    tick=0

                v += total_force * 0.9
                v *= 0.9
                t += v
            return t

        t = trilaterate(sliders)
        return t

def main():
    d = delta()

    t = d.fk(np.array([100,100,100]).astype('float32'))
    print(t)

if __name__ == '__main__':
    main()
