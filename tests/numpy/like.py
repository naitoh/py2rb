# coding: utf-8
import numpy as np

def print_matrix(data):
    data_i = []
    for i in list(data):
        data_j = []
        for j in i:
            data_j.append(int("%d" % j))
        data_i.append(data_j)
    print(data_i)

x = np.arange(6)
x = x.reshape(2, 3)
print_matrix(x)

x = np.ones_like(x)
print_matrix(x)

x = np.zeros_like(x)
print_matrix(x)

x = np.full_like(x, 1)
print_matrix(x)

a = ([1,2,3], [4,5,6])   
x = np.empty_like(a)
print(list(x.shape))

a = np.array([[1., 2., 3.],[4.,5.,6.]])
x = np.empty_like(a)
print(list(x.shape))
