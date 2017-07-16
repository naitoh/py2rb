import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))    

x = np.arange(-5.0, 5.0, 0.1)
y = sigmoid(x)
print(len(y))
