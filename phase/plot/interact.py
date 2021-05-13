from phase.plot.mpl import MPLPlot

import numpy as np
import time
import sys

class Interact(MPLPlot):
    def __init__(self):
        self.cur_frame_plt = []
        self.mouse_cid = self.figure.canvas.mpl_connect('button_press_event', self.onclick)
        self.release_cid = self.figure.canvas.mpl_connect('button_release_event', self.onrelease)
        self.key_cid = self.figure.canvas.mpl_connect('key_press_event', self.onpress)
        self.last_frame, self.press_time = -1, None
        self.run()
    def run(self):
        frame = input(self.prompt())
        while frame:
            self.plot_frame(int(frame))
            frame = input(self.prompt())
        else:
            input('[ Exit ]')
    def print_status(self, frame):
        sys.stdout.write('%d\n%s' % (frame, self.prompt()))
        sys.stdout.flush()
    def onclick(self, event):
        self.press_time = time.time()
    def onrelease(self, event):
        if self.is_event(event):
            frame = self.get_closest(event)
            self.print_status(frame)
            self.plot_frame(frame)
            self.raise_figure()
    def onpress(self, event):
        if event.key == 'right':
            frame = (self.last_frame+1) % len(self)
        elif event.key == 'left':
            frame = (self.last_frame-1) % len(self)
        else:
            return
        self.print_status(frame)
        self.plot_frame(frame)
        self.raise_figure()
    def is_event(self, event):
        if self.press_time is None or time.time() - self.press_time > 0.5:
            return False
        try:
            iter(self.axis)
        except TypeError:
            return event.inaxes == self.axis
        return any(event.inaxes == ax for ax in self.axis)
    def plot_frame(self, frame):
        pass
    def get_closest(self, event):
        pass
    def prompt(self):
        pass
    def plot_current(self, frame):
        pass
