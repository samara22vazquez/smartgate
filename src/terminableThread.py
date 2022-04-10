import threading
import config

'''Threads must be re-instantiated before restarting'''
class TerminableThread(threading.Thread):
    def __init__(self, name, target):
        config.set_to_start(name)
        threading.Thread.__init__(self, name=name, target = target)

    def end(self):
        if self.name in config.thread_end:
            config.set_to_end(self.name)
            threading.Thread.join(self)

    def run(self):
        if self.name in config.thread_end:
            config.set_to_start(self.name)
            super(TerminableThread, self).run()


