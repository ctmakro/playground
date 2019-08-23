incoming = 'G0 Xnone Y100 Z10'

splitted = incoming.split(' ')
d = {}

for string in splitted:
    d[string[0]] = string[1:]

print(d)

x = d['X']
y = d['Y']
z = d['Z']

x = float(x) if x is not None else None
