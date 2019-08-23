import cv2
from cv2tools import vis,filt
import numpy as np

from scipy.optimize import minimize

def stochastic_points_that_connects():
    # rule:
    # 1. sample 2 endpoint
    # 2. find their middlepoint
    # 3. repeat using the 2 endpoints of each of the 2 new segments.

    # minimum dist between two connected points
    mindist = 0.05

    # given two point, return their centerpoint.
    def get_stochastic_centerpoint(p1, p2):
        c = (p1+p2)*.5
        # dist = np.linalg.norm(p1-p2)
        dist = np.sqrt(np.sum(np.square(p1-p2)))
        if dist < mindist:
            return None
            # if two point already very close to each other,
            # don't insert a centerpoint between them
        else:
            c += np.random.normal(loc=0, scale=0.2*dist, size=c.shape)
            return c

    # insert a new point between every two previously connected points.
    def insert_between(points):
        newpoints = []
        for i in range(len(points)-1):
            p1 = points[i]
            p2 = points[i+1]
            newpoints.append(p1)
            cp = get_stochastic_centerpoint(p1, p2)
            if cp is not None:
                newpoints.append(cp)

        newpoints.append(p2)
        return newpoints

    while 1:
        points = [np.random.uniform(0,1,size=(2,)) for i in range(2)]

        for i in range(5):
            points = insert_between(points)

        # if the number of points included is larger than 4
        # we can return this as a legit polyline object
        if len(points)>4:
            return np.array(points)

        # otherwise we try again
        else:
            continue

# a group of points connected by lines
class Connected:
    def __init__(self, points=None):
        self.points = points

    def draw_on(self, canvas):
        cv2.polylines(
            canvas,
            [(self.points*16).astype(np.int32)],
            isClosed = False,
            color=(0, 0, 0),
            thickness=1,
            lineType=cv2.LINE_AA,
            shift = 4,
        )

    # penalties of various forms.
    def calc_penalty(self):
        # segment direction penalty: if connecting segments are facing different direction, give penalty.

        deltas = self.points[:len(self.points)-1] - self.points[1:]

        sq_norms = np.square(deltas[:,0]) + np.square(deltas[:,1])
        # # normalize the vectors.
        # norms = np.linalg.norm(deltas,axis=1,keepdims=True)
        # deltas = deltas / (norms + 1e-2)
        #
        # dot_products = np.sum(
        #     deltas[:len(deltas)-1] * deltas[1:],
        #     axis=1,
        # )
        #
        # # print(deltas.shape)
        # # print(dot_products.shape)
        #
        # limited = np.maximum(-dot_products, 0)
        # angular_pen = limited.mean()

        min_length = 2
        max_length = w
        clipped = np.clip(sq_norms, min_length*min_length, max_length*max_length)

        pen = np.mean(np.abs(sq_norms - clipped))
        return pen

        length_pen = np.maximum(min_length - sq_norms, 0).mean()
        length_pen += np.maximum(sq_norms - max_length, 0).mean()

        return angular_pen + length_pen


class ManyConnected:
    def __init__(self, w=None, num_segs=60):
        # w = width, indicate the range of coordinates of the lines

        self.list = []
        self.clist = []

        for i in range(num_segs):
            # self.add(Connected(stochastic_points_that_connects() * w))
            self.list.append(stochastic_points_that_connects() * w)

    def add(self, connected):
        self.list.append(connected.points)
        self.clist.append(connected)

    def draw_on(self, canvas):
        cv2.polylines(
            canvas,
            [(points*64).astype(np.int32) for points in self.list],
            isClosed = False,
            color=(0, 0, 0),
            thickness=1,
            lineType=cv2.LINE_AA,
            shift = 6,
        )

    # into vector that could be optimized
    def to_vec(self):
        a = np.vstack(self.list)
        return a.flatten()

    def from_vec(self, v):
        vc = v.copy()
        vc.shape = len(vc)//2, 2
        i = 0
        for points in self.list:
            l = len(points)
            points[0:l, 0:2] = vc[i:i+l, 0:2]
            # points[0:l] = vc[i:i+l]
            i+=l

    # penalties of various forms.
    def calc_penalty(self):
        return sum([c.calc_penalty() for c in self.clist]) / len(self.clist)

# canvas width
w = 256

def newcanvas():
    return np.ones((w,w,1), dtype='uint8')*255

mc = ManyConnected(w=w)

v = mc.to_vec()
print(type(v), v.shape)
mc.from_vec(v)

target = cv2.imread('hjt.jpg')
target = vis.resize_perfect(target, w, w, cubic=True, a=3)
target = (target/255.).astype('float32')
target = (target[:,:,1:2] + target[:,:,2:3]) *.5

target = np.clip(target*1+0.1, 0, 1)

def pyramid(img):
    a = [img]
    for i in range(5):
        a.append(cv2.pyrDown(a[-1]))
    return a

target_pyr = pyramid(target)

def multiscale_loss(canvas):
    canvas_pyr = pyramid((canvas/255.).astype('float32'))
    return sum([np.square((c-t)).mean() for c,t in zip(canvas_pyr, target_pyr)])

def singlescale_loss(canvas):
    return np.square(canvas.astype('float32')/255. - target).mean()

def to_optimize(v):
    mc.from_vec(v)
    nc = newcanvas()
    mc.draw_on(nc)
    ml = multiscale_loss(nc)
    # sl = singlescale_loss(nc)
    # pen = mc.calc_penalty()
    pen = 0

    return ml
    # return sl + pen * 0.001

import cProfile

def perf_debug():
    cProfile.run('optimize_for_target(it=50)', sort='tottime')

# exploit parallelism
from llll import MultithreadedMapper
mm = MultithreadedMapper(nthread=6)

def minimize_cem(fun, x, iters,
    survival=0.5,
    mutation=3.0, popsize=100, cb=None, mating=False):
    initial_mean = x
    initial_stddev = np.ones_like(initial_mean)*mutation

    def populate(size, mean, stddev):
        return [np.random.normal(loc=mean, scale=stddev)
            for i in range(size)]

    def mate(father, mother): # each being a vector
        m = (father + mother) * .5
        std = np.maximum(mutation, np.abs(father - mother) * 0.5)
        return np.random.normal(loc=m, scale=std)

    def populate_mate(size, parents):
        population = []
        lp = len(parents)
        for i in range(size):
            fa,mo = np.random.choice(lp,2,replace=False)
            population.append(mate(
                    parents[fa],parents[mo]
                ))
        return population

    initial_population = [initial_mean] + populate(
        popsize, initial_mean, initial_stddev)

    population = initial_population

    trace = []

    for i in range(iters):
        print('{}/{}'.format(i+1,iters))
        import time
        start = time.time()

        # evaluate fitness for all of population
        parallel = True
        if not parallel:
            fitnesses = [fun(v) for v in population]
        else:
            fitnesses = mm.map(fun, population) # faster on multicore

        mean_fitness = sum(fitnesses)/popsize

        # time it
        duration = time.time() - start
        time_per_instance = duration / popsize

        # sort according to fitness
        fitnesses_sorted = sorted(zip(fitnesses, population), key=lambda k:k[0])
        max_fitness = fitnesses_sorted[0][0]
        min_fitness = fitnesses_sorted[-1][0]

        tophalf = fitnesses_sorted[0:int(popsize*survival)] # top half

        # keep the params, discard the fitness score
        tophalf_population = [fp[1] for fp in tophalf]

        # mean and std of top half (for CEM)
        ap = np.array(tophalf_population)
        mean = np.mean(ap, axis=0)
        stddev = np.maximum(np.std(ap, axis=0), mutation)

        # keep the best
        best = tophalf_population[0]

        # keep the mean (better than best in some cases)
        population = [best, mean]

        if not mating: # CEM
            # fill the rest of population with offsprings of the top half
            population += populate(
                size=popsize-len(population),
                mean=mean, stddev=stddev,
            )
        else:
            tophalf_population.append(mean)

            # same but mate pairwise
            population = tophalf_population + populate_mate(
                size = popsize-len(tophalf_population),
                parents = tophalf_population,
            )

        assert len(population) == popsize

        # logging
        print('fitness: mean {:2.6f} (best {:2.6f} worst {:2.6f} out of {}) {:2.4f} s ({:2.4f}s/i, {:4.4f}i/s)'.format(
            mean_fitness, max_fitness, min_fitness,
            popsize,
            duration, time_per_instance, 1 / time_per_instance))

        log = {
            'best':best,
            'max_fitness': max_fitness,
            'mean':mean,
            'mean_fitness': mean_fitness,
        }
        trace.append(log)
        if cb is not None:
            cb(log)

    return {'x':best, 'trace':trace}

def run_cem_opt(it=100):
    initial_x = mc.to_vec()

    def callback(dic):
        mean = dic['mean']
        # display
        mc.from_vec(mean)
        show()

    results = [
    minimize_cem(
        to_optimize, initial_x,
        iters = it,
        mutation = 3.0,
        popsize=100,
        survival = 0.5,
        cb = callback,
    ),
    minimize_cem(
        to_optimize, initial_x,
        iters = it,
        mutation = 3.0,
        popsize=100,
        survival = 0.25,
        cb = callback,
    ),
    minimize_cem(
        to_optimize, initial_x,
        iters = it,
        mutation = 3.0,
        popsize=100,
        survival = 0.125,
        cb = callback,
    ),
    minimize_cem(
        to_optimize, initial_x,
        iters = it,
        mutation = 3.0,
        popsize=100,
        survival = 0.7,
        cb = callback,
        mating=True,
    ),
    minimize_cem(
        to_optimize, initial_x,
        iters = it,
        mutation = 3.0,
        popsize=100,
        survival = 0.5,
        cb = callback,
        mating=True,
    ),
    minimize_cem(
        to_optimize, initial_x,
        iters = it,
        mutation = 3.0,
        popsize=100,
        survival = 0.25,
        cb = callback,
        mating=True,
    ),
    ]

    # mc.from_vec(x1)
    # show()

    from matplotlib import pyplot as plt
    for i,res in enumerate(results):
        plt.plot([d['mean_fitness'] for d in res['trace']], label = str(i))
    plt.legend()
    plt.show()


def randomize():
    v = mc.to_vec()
    vc = np.random.normal(loc=v, scale=3)
    mc.from_vec(vc)
    # vcc = mc.to_vec()
    # assert ((vcc - vc)**2).sum() < 1e-10
    show()

def show():
    nc = newcanvas()
    mc.draw_on(nc)

    # nc2 = newcanvas()
    # [k.draw_on(nc2) for k in mc.clist]

    cv2.imshow('target', target)
    cv2.imshow('canvas', nc)
    # cv2.imshow('canvas2', nc2)
    cv2.waitKey(1)

show()
