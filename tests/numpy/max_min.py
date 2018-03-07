# coding: utf-8
import numpy as np

def print_matrix(data):
    data_i = []
    for i in list(data):
        data_j = []
        for j in i:
            data_j.append(j)
        data_i.append(data_j)
    print(data_i)

def print_array(data):
    datas = []
    for i in data:
        datas.append(i)
    print(datas)


x = np.array([2,3,4])
print_array(x)

z = np.array([[2,3,6],[3,4,5]])
print_matrix(z)

"""
max
"""
y = x.max()
print(y)
y = np.max([2, 3, 4])
print(y)

"""
amax
"""
y = np.amax([2, 3, 4])
print(y)

"""
max axis=0
"""
y = z.max(axis=0)
print_array(y)

"""
max axis=1
"""
y = np.max([[2,3,6],[3,4,5]], axis=1)
print_array(y)

"""
min
"""
y = x.min()
print(y)
y = np.min([2, 3, 4])
print(y)

"""
amin
"""
y = np.amin([2, 3, 4])
print(y)

"""
min axis=0
"""
y = z.min(axis=0)
print_array(y)

"""
min axis=1
"""
y = np.min([[2,3,6],[3,4,5]], axis=1)
print_array(y)

"""
max axis=0 keepdims
"""
y = np.max([[2,3,6],[3,4,5]], axis=0, keepdims=True)
print_matrix(y)

"""
min keepdims
"""
y = np.min([[2,3,6],[3,4,5]], keepdims=True)
print_matrix(y)
