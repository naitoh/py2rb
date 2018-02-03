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

def print_array(data):
    datas = []
    for i in data:
        if float("%.3f" % abs(i)) == 0:
            datas.append(float("%.3f" % abs(i)))
        else:
            datas.append(float("%.3f" % i))
    print(datas)

x = np.ones(5)
print_array(x)

x = np.zeros(5)
print_array(x)

x = np.full((2, 2), 1)
print_matrix(x)

#x = np.empty([2, 2])
#print(list(x.shape))


