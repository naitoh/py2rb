# coding: utf-8
import numpy as np

def print_array(data):
    datas = []
    for i in data:
        if float("%.3f" % abs(i)) == 0:
            datas.append(float("%.3f" % abs(i)))
        else:
            datas.append(float("%.3f" % i))
    print(datas)

x = np.arange(-5.0, 5.0, 0.1)
print(len(x))
print_array(list(x))

"""
maximum
"""
y = np.maximum(0, x)
print(len(y))
print_array(list(y))

"""
minimum
"""
y = np.minimum(0, x)
print(len(y))
print_array(list(y))
