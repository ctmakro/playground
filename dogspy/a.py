import os

dogdir = './downloads/dog faces'
dogdir_chosen = './downloads/dog faces chosen'

dogdir = './downloads/many dogs'
dogdir_chosen = './downloads/many dogs chosen'

pics = next(os.walk(dogdir))[2]

os.makedirs(dogdir_chosen, exist_ok=True)

pics = [l for l in pics if l.lower().endswith('.jpg')]

index = 0
length = len(pics)

print(len(pics), 'pics found')

d = {}

import cv2
from cv2tools import vis

def get_pic(name):
    if name not in d:
        fullpath = os.path.join(dogdir, name)
        img = cv2.imread(fullpath)

        if img is None:
            print('met None:', fullpath)
            raise

        d[name] = vis.autoscale(
            img,
            limit=400,
        )[0]
    return d[name]

from shutil import copyfile

while 1:
    try:
        cv2.imshow('', get_pic(pics[index]))
        print('pic {}/{} showing'.format(index+1, length))
    except:
        index = (index+1) % length
        continue

    k = cv2.waitKey(0)

    if k==ord('a'):
        index = (index - 1) % length
    if k==ord('d'):
        index = (index+1) % length
    if k==ord('t'):
        print('pic {} accepted'.format(index))

        copyfile(
            os.path.join(dogdir, pics[index]),
            os.path.join(dogdir_chosen, pics[index]),
        )

        index = (index+1) % length
    if k==ord('q'):
        break
