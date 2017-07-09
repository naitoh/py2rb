import os

for dirpath, dirnames, filenames in os.walk('tests/os/testdir'):
    print('<dirpath>')
    print(dirpath)
    print('<dirnames>')
    for dirname in dirnames:
        print(dirname)
    print('<filenames>')
    for filename in filenames:
        print(filename)
