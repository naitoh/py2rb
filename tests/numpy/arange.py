import numpy as np

def print_array(data):
    datas = []
    for i in data:
        if float("%.3f" % abs(i)) == 0:
            datas.append(float("%.3f" % abs(i)))
        else:
            datas.append(float("%.3f" % i))
    print(datas)

x = np.arange(-1.0, 1.0, 0.1)
print_array(x)
x = np.arange(6)
print_array(x)
x = np.arange(1,6) 
print_array(x)
x = np.arange(1,6,2)
print_array(x)

