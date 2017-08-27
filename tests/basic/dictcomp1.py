foo = {key.upper(): data * 2 for key, data in {'a': 7, 'b': 5}.items()}
print(foo['A'])
print(foo['B'])
