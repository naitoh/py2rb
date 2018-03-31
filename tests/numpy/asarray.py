import numpy as np

def print_matrix(data):
    data_i = []
    for i in list(data):
        data_j = []
        for j in i:
            data_j.append(int("%d" % j))
        data_i.append(data_j)
    print(data_i)

def print_array(data):
    datas = []
    for i in data:
        datas.append(float("%.3f" % i))
    print(datas)

x = np.asarray([[1.,2.],[3.,4.]])
print_matrix(x)

x = np.asarray([1.,2.])
print_array(x)

y = np.asarray([3.,4.])
print_array(y)

z = (x + y)[0]
print(z)
