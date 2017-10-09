# coding: utf-8
import numpy as np

v = np.any([[True, False], [True, True]])
print(str(v).upper())

""" [False, True] => [0, 1] """
v = np.any([[True, False], [True, True]], axis=0)
for a in v:
    if a in (True, 1):
        print('TRUE')
    else:
        print('FALSE')

v = np.any([-1, 0, 4])
print(str(v).upper())

v = np.any(np.nan)
print(str(v).upper())

