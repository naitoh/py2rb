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

x = np.full((2, 2), 5, dtype=np.int64)
print_matrix(x)

