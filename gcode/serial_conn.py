import serial,time,math

class kossel:
    def __init__(self):
        self.ser = serial.Serial('COM11',250000,timeout=0.2)
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

def main():
    with open('proby.gcode','r') as f:
        probing_code = f.read()

    k = kossel()
    print('KOSSEL READY')

    def run_gcode_collect_lines(filename):
        with open(filename,'r') as f:
            gcode = f.read().split('\n')

        gcode = filter(lambda x:len(x)>0, gcode)

        result_lines = []
        for line in gcode:
            result_lines+=k.command_ok(line,300)

        return result_lines

    gcode_result = run_gcode_collect_lines('proby.gcode')
    probing_result = list(filter(lambda x:x[0:3]=='Bed', gcode_result))

    print(probing_result)
    del k


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
