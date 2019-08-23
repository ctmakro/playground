import argparse as a

p = a.ArgumentParser()
p.add_argument('file', help='Filename')
args = p.parse_args()

# print(args)

fn = args.file

with open(fn, 'r') as f:
    csv = f.read()

csv = csv.split('\n')[1:-1]
csv = [[j.strip().replace('"','') for j in i.split(',')] for i in csv]

from collections import namedtuple

part = namedtuple('part',['symbol', 'value', 'package'])

for i in csv:
    while len(i)<3:
        i.append('')

csv = [part(symbol=i[0], value=i[1], package=i[2]) for i in csv]

for p in csv:
    print(p)

d = {}
m = {}
for part in csv:
    key = part.value+'__'+part.package
    if key in d:
        d[key]+=1
        m[key].append(part)
    else:
        d[key]=1
        m[key]=[part]

fn = fn.replace('.', '_aggergrated.')

f =open(fn,'w')

for k in d:
    parts = m[k]
    line = '{}, {}, {}, {}'.format(
        ' '.join([p.symbol for p in parts]),
        parts[0].value,
        parts[0].package,
        str(d[k]),
    )

    print(line)
    f.write(line+'\n')

print('saving to', fn)
