# coding: utf-8
import numpy as np

v = np.all([[True, False], [True, True]])
print(str(v).upper())

""" [True, False] => [1, 0] """
v = np.all([[True, False], [True, True]], axis=0)
for a in v:
    if a in (True, 1):
        print('TRUE')
    else:
        print('FALSE')

v = np.all([-1, 0, 4])
print(str(v).upper())

v = np.all([1.0 ,np.nan])
print(str(v).upper())

