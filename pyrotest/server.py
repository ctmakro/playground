from pyro_helper import *
import time

class Greeter:
    def __init__(self):
        import threading as th
        self.lock = th.Lock()
        self.counter = 0
    def selfadd(self,inp):
        self.lock.acquire()
        self.counter+=1

        c = self.counter
        self.lock.release()
        time.sleep(3)
        return inp+inp+str(c)

def main():
    pyro_expose(Greeter,65432,'greeter')

if __name__=="__main__":
    main()
