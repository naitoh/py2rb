

class foobar(object):
    
    x = 1

    def __init__(self):
        self.foovar = 1

    def bar(self, y=0):
        print(self.foovar + y)

f = foobar()
a = 'bar'

getattr(f, 'bar')(y=1)
getattr(f, a)()
print(getattr(f, 'x'))
print(getattr(f, 'z', 'Nothing'))
