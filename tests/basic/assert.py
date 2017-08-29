try:
    assert True, "no message"
except AssertionError as err:
    print('AssertionError :', err)
except:
    print('Error :')

try:
    assert False, "error message"
except AssertionError as err:
    print('AssertionError :', err)
except:
    print('Error :')
