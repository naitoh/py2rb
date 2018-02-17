import numpy as np

def print_array(data):
    datas = []
    for i in data:
        datas.append(i)
    print(datas)

x = np.array([1, 2, 3])
print_array(x)
y = np.copy(x)
print_array(y)
x[0] = 10
print_array(x)
print_array(y)

