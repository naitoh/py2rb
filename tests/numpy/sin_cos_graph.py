# coding: utf-8
import numpy as np

x = np.arange(0, 6, 0.1)
y1 = np.sin(x)
y2 = np.cos(x)

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
print(len(y1))
print_array(list(y1))
print(len(y2))
print_array(list(y2))
