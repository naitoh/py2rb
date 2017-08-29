try:
    raise
except:
    pass

try:
    foo
except NameError:
    print('NameError :')
except:
    print('Error :')

try:
    raise NameError
except NameError:
    print('NameError :')
except:
    print('Error :')

try:
    raise NameError('User Defined Error Message.')
except NameError as err:
    print('NameError :', err)
except:
    print('Error :')

try:
    raise NotImplementedError('User Defined Error Message.')
except NotImplementedError as err:
    print('NotImplementedError :', err)
except:
    print('Error :')
