

class A1(object):
    
    @staticmethod
    def msg(val):
        print("A1 static method msg says:"+str(val))

class A2(A1):
    pass

a = A2()

a.msg("hello")
A2.msg("world")
