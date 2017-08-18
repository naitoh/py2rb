
class wrapper:

    def __init__(self,fn):
        self.fn = fn

    def __call__(self,*args):
        return "(" + self.fn(*args) + ")"

def mydecorator(x):
    print("decorating " + str(x)) 
    return wrapper(x)

@mydecorator
def describe():
    return "world"
describe = mydecorator(describe)

print(describe())
