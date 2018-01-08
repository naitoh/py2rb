def list1(n):
    a = []
    a.append(1)
    a.append(2)
    a.append(3)
    a.append(n)
    return a[0] + a[1] + a[2] + a[3]

def list2():
    a = list(range(5))
    return str(a)

def list3():
    a = list(range(5))
    a[0] = 5
    a[4] = 0
    return str(a)

def list4():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[2:4]

def list5():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[:4]

def list6():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[1:6:2]

def list7():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[:]

def list8():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[::]

def list9():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[4:]

def list10():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[::2]

def list11():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[1::2]

def list12():
    a = [8, 9, 10, 11, 12, 13, 14]
    return a[:4:2]

print(list1(4))
print(list1(5))
print(list2())
print(list3())
print(list4())
print(list5())
print(list6())
print(list7())
print(list8())
print(list9())
print(list10())
print(list11())
print(list12())
