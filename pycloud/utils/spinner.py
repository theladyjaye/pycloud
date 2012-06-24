class Spinner(object):
    def __init__(self):
        self.parts = ['|', '/', '-']
        self.current_index = 0
        self.parts_length = len(self.parts)

    def __iter__(self):
        return self;

    def next(self):
        if self.current_index == (self.parts_length -1):
            self.current_index = 0
        else:
            self.current_index += 1
        
        return self.parts[self.current_index]
    
        
