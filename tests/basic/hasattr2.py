class AttrTest():
    def __init__(self):
        self.base = -1

attr_test = AttrTest()
attr_test.foo = 'python-attr'
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
