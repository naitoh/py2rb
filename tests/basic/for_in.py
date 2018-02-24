# iterating over a list
print('-- list --')
a = [1,2,3,4,5]
for x in a:
    print(x)

# iterating over a tuple
print('-- tuple else case --')
a = ('cats','dogs','squirrels')
for x in a:
    print(x)
else:
    print('ok')

print('-- tuple else break case --')
for x in a:
    print(x)
    if x == 'squirrels':
        break
else:
    print('ok')

# iterating over a dictionary
# sort order in python is undefined, so need to sort the results
# explictly before comparing output

print('-- dict keys --')
a = {'a':1,'b':2,'c':3 }

keys = []
for x in a.keys():
    keys.append(x)

keys.sort()
for k in keys:
    print(k)

print('-- dict values --')
values = list()
for v in a.values():
    values.append(v)

values.sort()
for v in values:
    print(v)

items = dict()
for k, v in a.items():
    items[k] = v

print('-- dict item --')
print(items['a'])
print(items['b'])
print(items['c'])

# iterating over a string
print('-- string --')
a = 'defabc'
for x in a:
    print(x)

