import autograd.numpy as np  # Thinly-wrapped numpy
from autograd import grad, elementwise_grad as egrad, value_and_grad as vgd
    # The only autograd function you may ever need

def tanh(x):                 # Define a function
    y = np.exp(-2.0 * x)
    return (1.0 - y) / (1.0 + y)

# print(tanh(1.0))

def gradn(f, n):
    for i in range(n):
        f = grad(f)
    return f

for i in range(6):
    print(gradn(tanh,i)(1.0))

def mul(a,b):
    return a*b

print(grad(mul)(2.,3.))


# let's solve the two beam problem.

r2 = np.sqrt(2)/2
# node 2 target force: x 0 y -1N
n2tf = np.array([0., -1.])
# deltal =  f * k
k = 0.001 # m/N, softness
st = 1000 # N/m, stiffness (of rod)


def twobeam(x):
    # strain of the 2 elements. x0 higher x1 lower
    e0l = x[0]; e1l = x[1]

    # node 0: upper fixed
    # node 1: lower fixed
    # node 2: far end

    # element 0 force: e0f = e0l / k
    e0f = e0l * st
    e1f = e1l * st


    # node 2 actual force:
    # n2f = e0f * np.array([-r2, r2]) + e1f * np.array([-r2, -r2])
    n2f = e0f * np.array([-r2, r2]) + e1f * np.array([-1, 0])

    err = np.sum(np.square((n2f + n2tf)))
    return err

# print(twobeam(np.array([0.01, -0.01])))

def minimize(f, ix):
    gf = grad(f)

    x = ix

    stepsize = 0.00005

    lastv = 1

    for i in range(100):
        v = f(x)

        if v < 1e-16:
            break

        g = gf(x)
        # print('g:',g)


        # if v > lastv: # error got larger
        #     stepsize *= 0.13 # smaller stepsize
        # else:
        #     stepsize *= 2.1

        trend = v / lastv  # >1 means error increased
        if 1:
            if trend > 10:
                stepsize *= 0.01
            elif trend > 1.1:
                stepsize *= 0.2
            elif trend <0.2:
                stepsize *= 1.5
            elif trend <0.95:
                stepsize *= 1.5
            else:
                pass

        # stepsize = stepsize * trend * (0.2 if trend<1 else 2)

        print('[{:3d}]v:{:.1e} trend:{:.2f} ss:{:.1e} x:{}'.format(i,v,trend,stepsize,x))

        x -= g * stepsize # gradient descent!
        lastv = v

    return x

solvedx = minimize(twobeam, np.array([0., 0.]))

# forces
print(solvedx * st)
