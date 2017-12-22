
def func():
    yield 1, 2
    yield 2
    yield 3

gen = func()

print(gen.__next__())
print(gen.__next__())
print(gen.__next__())
