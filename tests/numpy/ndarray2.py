import numpy
from numpy import ndarray

a = numpy.array([1,2,3,4,5], dtype='int8')
if isinstance(a, ndarray):
    print('OK')
else:
    print('NG')

