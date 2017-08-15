
l = [4,7,3,4,2,1]
v = all(l)
print(str(v).upper())

print(str(all([])).upper())
print(str(all({})).upper())
print(str(all(())).upper())
print(str(all([False])).upper())
print(str(all([None])).upper())
print(str(all([0])).upper())
print(str(all([''])).upper())
print(str(all([[]])).upper())
print(str(all([{}])).upper())

l = [0,{}]
v = all(l)
print(str(v).upper())
