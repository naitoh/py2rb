class AttrTest():
    def __init__(self):
        self.base = -1

    def __call__(self):
        if hasattr(self, 'base'):
            print("Class :base is True")
        else:
            print("Class :base is False")

attr_test = AttrTest()
if hasattr(attr_test, 'base'):
    print("base is True")
else:
    print("base is False")

if hasattr(attr_test, 'foo'):
    print("foo is True")
else:
    print("foo is False")

if hasattr(attr_test, 'bar'):
    print("bar is True")
else:
    print("bar is False")
attr_test()
