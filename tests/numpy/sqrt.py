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

""" Math functions """

x1 = np.arange(0, 6, 0.1)


y1 = np.sqrt(x1)

for y in [x1]:
    print(len(y))
    print_array(list(y))
