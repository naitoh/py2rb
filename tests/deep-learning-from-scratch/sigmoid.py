import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))    

x = np.arange(-5.0, 5.0, 0.1)
y = sigmoid(x)

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
