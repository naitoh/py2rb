# coding: utf-8
import numpy as np

def relu(x):
    return np.maximum(0, x)

x = np.arange(-5.0, 5.0, 0.1)
y = relu(x)
print(len(y))
print(np.maximum(0, 1))
