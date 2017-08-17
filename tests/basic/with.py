with open("hello.txt", 'w') as f:
    f.write("Hello, world!")

with open("hello.txt", 'r') as f:
    print(f.read())

with open("hello.txt", 'r'):
    print('ok')
