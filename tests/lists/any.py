
l = [4,7,3,4,2,1]
v = any(l)
print(str(v).upper())

print(str(any([])).upper())
print(str(any({})).upper())
print(str(any(())).upper())
print(str(any([False])).upper())
print(str(any([None])).upper())
print(str(any([0])).upper())
print(str(any([''])).upper())
print(str(any([[]])).upper())
print(str(any([{}])).upper())

l = [0,{}]
v = any(l)
print(str(v).upper())
