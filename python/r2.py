
def phi(d):
    power = 1/(d+1)
    x = 1
    while 1:
        k = pow(x+1, power)
        if k == x:
            break
        else:
            x = k
    return x

# print(phi(1))

import numpy as np
import random

class LowDiscrepancyGenerator:
    def __init__(self, d):
        self.phi = phi(d)
        self.d = d

        self.a = np.array([1/pow(self.phi,i+1) for i in range(d)])
        self.x = np.ones_like(self.a)/2

    def one(self):
        for i in range(1):
            self.x = (self.x + self.a) % 1.0
        return self.x

LDG = LowDiscrepancyGenerator

ldg = LDG(2)
for i in range(10):
    print(ldg.one())

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

# print(list(zip(*[[1,2],[3,4]])))

for i in range(10):
    plt.scatter(*list(zip(*[ldg.one() for i in range(100)])))
plt.show()
