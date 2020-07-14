import numpy as np

na = np.array

v1 = na([1., 1., 1.])

v2 = na([2., 1.44, 6])

def norm(v):
    return np.sqrt(np.sum(np.square(v)))

def normalize(v):
    return v/norm(v)

# print(1, normalize(na([3., 4.])))

v2 = normalize(v2)

# print(v2)

prod = v1
for i in range(10):
    print(norm(prod), prod)
    # prod *= v2
    # prod = np.matmul(prod, v2)
    prod =  np.cross(prod,v2)/(norm(v1))

# for i in range(10):
#     print(norm(prod), prod)
#     # prod *= v2
#     # prod = np.matmul(prod, v2)
#     prod = np.cross(prod, -v2)*1.5

print(prod)
