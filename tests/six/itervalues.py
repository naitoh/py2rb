import six

foo = { 'a':'b' }

for f in six.itervalues(foo):
    print(f)

