
class Spam(object):

    def __init__(self,value):
        self.value = value

class Eggs(object):

    def __init__(self,value):
        self.value = value

s = Spam(1)
e = Eggs(2)

if isinstance(s,Spam):
    print("s is Spam - correct")

if isinstance(s,Eggs):
    print("s is Eggs - incorrect")

if isinstance(e,Spam):
    print("e is Spam - incorrect")

if isinstance(e,Eggs):
    print("e is Eggs - correct")

if isinstance(1, int):
    print("int - correct")

if isinstance(0.1, float):
    print("float - correct")

if isinstance('str', str):
    print("str - correct")

if isinstance([0], list):
    print("list - correct")

if isinstance((0, 1), tuple):
    print("tuple - correct")

if isinstance({'a': 1}, dict):
    print("dict - correct")
