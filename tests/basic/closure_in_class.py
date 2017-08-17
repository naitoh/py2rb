
class foo(object):

    def factory(self, x):

        def fn():
            return x

        return fn

f = foo()


a1 = f.factory("foo")
a2 = f.factory("bar")
print(a1())
print(a2())
