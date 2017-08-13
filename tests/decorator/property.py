class propertyDecorator(object):
    def __init__(self, x):
        self._x = x

    @property
    def x(self):
        return self._x

pd = propertyDecorator(100)
print(pd.x)

