import serial,time,math

import binascii

uh = lambda h:binascii.unhexlify(h)

def choose_serial_connection():
    import serial.tools.list_ports as stlp

    l = stlp.comports()
    if len(l) == 0:
        raise Exception('No available serial devices found')

    print('Please choose from the following serial ports.')
    for i,s in enumerate(l):
        print('({}) {}'.format(i,s))

    k = input('Please enter a number [{}-{}]'.format(0, len(l)-1))
    if len(k)==0: k=0
    return l[int(k)].device


print(uh('909301'))

ser = serial.Serial(choose_serial_connection(),115200,timeout=0.2)


def wc(h):
    cmd = ('fa af 01'+h+'a7 ed').replace(' ','')
    print(cmd)
    cmd = uh(cmd)
    par = bytes([sum(cmd[2:-2]) % 256])
    # print(par)
    cmd = cmd[:-2] +par+ cmd[-1:]
    # cmd[-2] = par
    # print(cmd)

    ser.write(cmd)

# ser.write(uh('faaf01015a190032a7ed'))

# ser.write(uh('faaf01015a190032a7ed'))

# wc('01 5a 19 00 32')
# wc('01 4a 19 00 32')
# move tarpos, time, time, time

def i2h(i):
    return '{:02x}'.format(i)

def gopos(deg, t=0, t1=0, t2=0):

    wc('01' + i2h(deg) + i2h(t)+i2h(t1)+i2h(t2))
    ser.flush()


# for i in range(0,255,5):
#     gopos(i, t2=0)
#     time.sleep(0.05)

while 1:
    splits = 512
    for i in range(splits):
        k = i/splits*2*math.pi
        p = math.cos(k)*90+90
        gopos(int(p), t=0)
        time.sleep(0.01)


# gopos(0,0)
# time.sleep(1)
# gopos(180,0)
# time.sleep(1)
# gopos(0,0)
# time.sleep(1)


time.sleep(1)
