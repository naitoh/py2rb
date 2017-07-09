

x = { 'foo':'bar','aaa':'bbb','xyz':'zyx','spam':'eggs' }

s = list(x.keys())
s.sort()
for k in s:
    print(k + " -> " + x[k])
