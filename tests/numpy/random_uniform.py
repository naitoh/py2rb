import numpy as np

def print_matrix(data):
    data_i = []
    for i in list(data):
        data_j = []
        for j in i:
            data_j.append(j)
        data_i.append(data_j)
    print(data_i)

x = np.random.uniform(-1, 1, (3,2))

y = np.array(x < 1, dtype=np.int)
print_matrix(y)

y = np.array(x > -1, dtype=np.int)
print_matrix(y)

x = np.random.uniform(-1, 1)
x = np.asarray(x)
print(x.ndim)

