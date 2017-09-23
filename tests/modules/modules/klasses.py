
class Baseklass(object):

    @staticmethod
    def sayhello():
        print("baseklass says hello")

class Klass(Baseklass):

    pass


if __name__ == '__main__':

    k = Klass()
    k.sayhello()
    Klass.sayhello()
    Baseklass.sayhello()
