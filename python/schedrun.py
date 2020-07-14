import time,os,sched,threading,traceback,datetime

def failwhy(k):
    try:
        k()
    except:
        traceback.print_exc()

def schedrun(f,interval):
    sch = sched.scheduler(time.time,time.sleep)

    def ff():
        failwhy(f)

    def start_scheduled_execution():
        t = time.time()

        while 1:
            event = sch.enterabs(t+interval, 0, ff)
            sch.run()
            t+=interval

    th = threading.Thread(target=start_scheduled_execution, daemon=True)
    th.start()
