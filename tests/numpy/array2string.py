import numpy as np

x = np.array([1,2,3,4,5,6,7,8,9,10], dtype='int8')
print(list(x))
print(np.array2string(x))
print(np.array2string(x, None))
print(np.array2string(x, None, None, None, ' '))
print(np.array2string(x, precision=2, separator=',', suppress_small=True))
print(np.array2string(x, precision=3, separator=',', suppress_small=True))
print('hoge : ' +np.array2string(x, precision=4, separator=',', suppress_small=True, prefix='hoge : '))
print(np.array2string(x, precision=4))
print(np.array2string(x))
