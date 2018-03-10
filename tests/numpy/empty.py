# coding: utf-8
import numpy as np

def print_array(data):
    datas = []
    for i in data:
        datas.append(i)
    print(datas)

x = np.empty(())
print_array(x.shape)

x = np.empty((0))
print_array(x.shape)

x = np.empty((0,0))
print_array(x.shape)

x = np.empty(3, dtype=np.float32)
print_array(x.shape)

x = np.empty((2,3))
print_array(x.shape)

