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
        datas.append(int("%d" % i))
    print(datas)

x = np.asarray([[1,2,3],[4,5,6]])
print_matrix(x)

"""
x[0,:]
"""
print_array(x[0,:])

"""
x[1,1:]
"""
y = x[1,1:]
print_array(y)

"""
x[1,:2]
"""
x[1,:2] = 5
print_array(y)
print_matrix(x)

x = np.asarray([[1,2,3],[4,5,6]])
print_matrix(x)

"""
x[:,0]
"""
print_array(x[:,0])

"""
x[:,1]
"""
print_array(x[:,1])

x = np.asarray([[[1,2,3],[4,5,6]],[[11,12,13],[14,15,16]]])
#print_matrix(x)

"""
x[0,:] Not Support

It is not supportable if the number of arguments and the number of dimensions are different.

print_matrix(x[0,:])
"""

"""
x[0,1,:]
"""
print_array(x[0,1,:])
