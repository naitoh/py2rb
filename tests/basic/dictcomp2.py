foo = {key.upper(): data * 2 for key, data in {'a': 7, 'b': 5}.items() if data > 6}
print(len(foo))
print(foo['A'])
