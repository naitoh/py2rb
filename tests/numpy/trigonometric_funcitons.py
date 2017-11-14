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

""" Trigonometric functions """

x1 = np.arange(0, 6, 0.1)
x2 = np.arange(-0.9, 1, 0.1)
x3 = np.arange(1, 6, 0.1)

y1 = np.sin(x1)
y2 = np.cos(x1)
y3 = np.tan(x1)

yh1 = np.sinh(x1)
yh2 = np.cosh(x1)
yh3 = np.tanh(x1)

ay1 = np.arcsin(x2)
ay2 = np.arccos(x2)
ay3 = np.arctan(x1)

ayh1 = np.arcsinh(x1)
ayh2 = np.arccosh(x3)
ayh3 = np.arctanh(x2)

for y in [x1, x2, x3, y1, y2, y3, yh1, yh2, yh3, ay1, ay2, ay3, ayh1, ayh2, ayh3]:
    print(len(y))
    print_array(list(y))
