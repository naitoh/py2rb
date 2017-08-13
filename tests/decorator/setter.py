class propertyDecorator(object):
    def __init__(self, x):
        self._x = x

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

pd = propertyDecorator(100)
print(pd.x)
pd.x = 10
print(pd.x)

