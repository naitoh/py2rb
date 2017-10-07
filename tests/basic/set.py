# iterating over a list
print('-- set --')
a = set([1,2,3,4,5])
a.remove(3)
for x in a:
    print(x)

print('-- set add --')
a = set()
a.add(1)
a.add(2)
a.add(1)
for x in a:
    print(x)

print('-- set clear --')

a.clear() 
for x in a:
    print(x)
