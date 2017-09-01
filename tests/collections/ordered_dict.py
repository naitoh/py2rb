import collections


d = collections.OrderedDict({'one': 1, 'two':2, 'three':3})
print(d['one'])
print(d['two'])
print(d['three'])

e = collections.OrderedDict(d)
print(e['one'])
print(e['two'])
print(e['three'])
#d = collections.OrderedDict(one=1, two=2, three=3)
#print(d['one'])
#print(d['two'])
#print(d['three'])
