import serial,time,math

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

class kossel:
    def __init__(self):
        self.ser = serial.Serial(choose_serial_connection(),250000,timeout=0.2)
        print('(kossel)serial name: ',self.ser.name)
        self.linenumber = 0

        time.sleep(1)
        self.waitready()

    def readline(self):
        b = self.ser.readline()
        # print(b)
        return b.decode('ascii')[:-1]

    def command(self,string):
        print('(kossel) SENT: '+string)

        b = (string+'\n').encode('ascii')
        # print(b)
        self.ser.write(b)
        self.ser.flush()

        self.linenumber+=1

    def wait(self, string, timeout=None, length=0):
        current = time.time()
        collected_lines = []
        print('(kossel) waiting for "'+ string+'"')
        while 1:
            if timeout is not None:
                if time.time() - current > timeout:
                    raise Exception('(kossel) waited longer than '+str(timeout))

            line = self.readline()
            if len(line)>0:
                current = time.time()
                print('(kossel) RECV: '+line)
                collected_lines.append(line)
                if (length==0 and line == string) or (length>0 and line[0:length] == string):
                    return collected_lines
            else:
                # print('(kossel) pyserial receive timeout')
                # print('.')
                pass

    def waitok(self,timeout=None):
        return self.wait('ok',timeout)

    def waitready(self):
        while 1:
            try:
                self.command('M105')
                self.wait('ok T', 1, length=4)
            except Exception as e:
                print(e)
            else:
                return

    # send command and wait for ok.
    def command_ok(self,c,timeout=None):
        self.command(c)
        return self.waitok(timeout)

global kos
kos = kossel()
def get_kossel():
    global kos
    return kos

def readfile(filename):
    with open(filename,'r') as f:
        content = f.read()
    return content

def run_gcode_collect_lines(gcode):
    gcode = gcode.split('\n')
    gcode = filter(lambda x:len(x)>0, gcode)

    k = get_kossel()
    print('KOSSEL READY')

    result_lines = []
    for line in gcode:
        result_lines+=k.command_ok(line,300)

    del k
    return result_lines

def main():
    gcode_result = run_gcode_collect_lines(readfile('proby.gcode'))
    probing_result = list(filter(lambda x:x[0:3]=='Bed', gcode_result))

    print(probing_result)

    idx = 0
    def getline():
        nonlocal idx,probing_result
        l = probing_result[idx]
        idx+=1
        return l

    probing_result+=['']
    saveto = 'probing_result.txt'
    with open(saveto,'w') as f:
        for l in probing_result:
            f.write(l+'\n')

    from prob_proc import plotfromfile
    plotfromfile(saveto)

if __name__ == '__main__':
    main()
