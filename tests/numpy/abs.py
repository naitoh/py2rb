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


"""
1-dim
"""
x = np.array([2,-3,4])
print_array(x)

y = np.abs(x)
print_array(y)

y = np.absolute(x)
print_array(y)
"""
2-dim
"""
z = np.array([[-2,3,-6],[3,-4,5]])
print_matrix(z)

y = np.abs(z)
print_matrix(y)

