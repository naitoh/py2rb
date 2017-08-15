# coding: utf-8
import numpy as np

def relu(x):
    return np.maximum(0, x)

x = np.arange(-5.0, 5.0, 0.1)
y = relu(x)

def print_array(data):
    datas = []
    for i in data:
        if float("%.3f" % abs(i)) == 0:
            datas.append(float("%.3f" % abs(i)))
        else:
            datas.append(float("%.3f" % i))
    print(datas)

print(len(x))
print_array(list(x))
print(len(y))
print_array(list(y))

print(np.maximum(0, 1))
