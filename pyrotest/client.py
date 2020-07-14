from pyro_helper import *

def main():

    def greet():
        Greeter = pyro_connect('localhost:65432','greeter')
        print(Greeter.selfadd('one'))

    import threading as th
    ts = [th.Thread(target=greet,daemon=True) for i in range(2)]

    for i in ts:
        i.start()

    for i in ts:
        i.join()

    # print(Greeter.selfadd('one'))

if __name__=="__main__":
    main()
