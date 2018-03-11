import numpy as np

def print_array(data):
    datas = []
    for i in data:
        datas.append(i)
    print(datas)

x = np.random.randint(3)
if 0 <= x <= 3:
    print('OK')
else:
    print('NG')

x = np.random.randint(1,3)
if 1 <= x <= 3:
    print('OK')
else:
    print('NG')

x = np.random.randint(1,3,(3,3))
print(x.ndim)
print_array(x.shape)

x = np.random.randint(1,3,(3,3), dtype=np.int64)
print(x.ndim)
print_array(x.shape)
