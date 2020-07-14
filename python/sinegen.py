import math

print('const PROGMEM int sinetable[512] = {')

n = 256
for i in range(n):
    j = i/n * math.pi * 2

    k = 0.2 * math.sin(j) + 0.5
    k = k*(1024-100)+50

    k = int(k)
    print(k, ',')

print('};')

for i in range(32):
    print(i,i*.61803398875)
