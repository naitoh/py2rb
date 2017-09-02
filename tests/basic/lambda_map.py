ary =[1, 2]
print([x**2 for x in ary])

print([x**2 for x in [1,2]])

print(list(map(lambda x: x ** 2, ary)))
print(list(map(lambda x: x ** 2, [1,2])))
