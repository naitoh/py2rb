# iterating over a list
print('-- list --')
a = [1,2,3,4,5]
for x in a:
    print(x)

# iterating over a tuple
print('-- tuple --')
a = ('cats','dogs','squirrels')
for x in a:
    print(x)

# iterating over a dictionary
# sort order in python is undefined, so need to sort the results
# explictly before comparing output

print('-- dict  --')
a = {'a':1,'b':2,'c':3 }

keys = []
for x in a:
    keys.append(x)

keys.sort()
for k in keys:
    print(k)

# iterating over a string
print('-- string --')
a = 'defabc'
for x in a:
    print(x)

