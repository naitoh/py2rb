def ifs1(x):
    a = 1
    if 0 < x < 10:
        a = 2
    else:
        a = 3
    return a

def ifs2(x):
    a = 1
    if 0 == x != 10:
        a = 2
    else:
        a = 3
    return a

def ifs3(x):
    a = 1
    if 0 in x in [[0]]:
        a = 2
    else:
        a = 3
    return a

print('ifs1')
print(ifs1(-1))
print(ifs1(1))
print(ifs1(11))
print('ifs2')
print(ifs2(0))
print(ifs2(10))
print('ifs3')
print(ifs3([0]))
print(ifs3([1]))
