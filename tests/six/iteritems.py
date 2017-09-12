import six

a = {'a':1,'b':2,'c':3 }

items = dict()
for k, v in six.iteritems(a):
    items[k] = v

print(items['a'])
print(items['b'])
print(items['c'])
