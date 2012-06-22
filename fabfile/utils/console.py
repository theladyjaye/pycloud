import sys

class Console(object):
    def __init__(self):
        pass

    def write(self, value):
        sys.stdout.write("\r" + value)
        sys.stdout.flush()

    def write_ln(self, value):
        print(value)