import numpy as np

def print_array(data):
    datas = []
    for i in data:
        datas.append(i)
    print(datas)
def print_matrix(data):
    data_i = []
    for i in list(data):
        data_j = []
        for j in i:
            data_j.append(j)
        data_i.append(data_j)
    print(data_i)

x = np.array([[1, 1], [2, 2], [3, 3]], dtype=np.int8)
"""[[1, 1], [2, 2], [3, 3]] => [1, 5, 1, 2, 2, 3, 3]"""
x = np.insert(x, 1, 5)
print_array(x)

x = np.array([[1, 1], [2, 2], [3, 3]])
"""[[1, 1], [2, 2], [3, 3]] => [[1, 5, 1], [2, 5, 2], [3, 5, 3]]"""
x = np.insert(x, 1, 5, axis=1)
print_matrix(x)
