import numpy as np

def normalized(v):
    norm = np.sqrt(np.sum(v**2))
    return v / norm

# Trilateration to find the target point, given positions of 3 points, and distances(radiuses)
def trilaterate(points, distances):
    precision = 1e-3
    iteration = 1000

    # points -> list of numpy vectors
    # distances -> list of distances
    # t -> initial guess
    t = np.array([0,0,-10]).astype('float32')

    # v -> initial velocity
    v = t*0

    for i in range(iteration):
        # print('t@',i,t)
        total_force = v*0
        tick = 0
        for idx in range(len(points)):
            direction = points[idx] - t # direction vector from t to sphere center
            dist_diff = (np.sqrt(np.sum(direction**2)) - distances[idx]) # distance difference

            force = dist_diff * normalized(direction)
            total_force += force

            if abs(dist_diff) < precision:
                tick+=1

        if tick>=len(points):
            break
        else:
            tick=0

        v += total_force # spring
        v *= 0.9 # damping
        t += v
    print('took',i+1,'iteration to solve trilateration')
    return t
