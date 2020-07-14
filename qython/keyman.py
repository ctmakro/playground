
import time
from pynput import keyboard

class KeyInterceptor:
    def __init__(self):
        self.pflag=False
        self.rflag=False

        self.kbc = keyboard.Controller()
        self.kbl = keyboard.Listener(
            on_press=lambda k: self.on_press(k),
            on_release=lambda k: self.on_release(k),
            suppress=True,
        )
        self.kbl.start()

    def press(self, key):
        self.pflag = True
        self.kbc.press(key)

    def release(self, key):
        self.rflag = True
        self.kbc.release(key)

    def on_press(self, key):
        print('-')
        if self.pflag:
            self.pflag = False
            return

        print(key,'pressed')
        self.press(key)
        return key

    def on_release(self, key):
        if self.rflag:
            self.rflag = False
            return

        self.release(key)
        return key

ki = KeyInterceptor()
time.sleep(3)
# listener.join()
