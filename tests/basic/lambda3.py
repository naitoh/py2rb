a = 5
def foo(x, y):
    x(y)

foo(lambda x: print(a), a)
