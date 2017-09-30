import numpy as np

print(str(0 * np.nan).lower())
if np.nan == np.nan: # False
    print("True")
else:
    print("False")

if np.inf > np.nan: # False
    print("True")
else:
    print("False")
print(str(np.nan - np.nan).lower())
