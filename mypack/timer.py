import time


class Timer:

    def __init__(self, precision=2):
        self.start_time()
        self.precision = precision

    def start_time(self):
        self.start = time.time()

    def elapsed_time(self):
        return round(time.time() - self.start, self.precision)

    def end_time(self):
        end_t = time.time() - self.start
        self.start = time.time()
        return round(end_t, self.precision)