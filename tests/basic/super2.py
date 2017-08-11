

class baseklass(object):

    def __init__(self,bval):
        self.bval = bval

    def describe(self,arg):
        print("baseklass.describe:"+self.bval+":"+str(arg))

    def describe2(self,**kwargs):
        print("baseklass.describe2:"+self.bval+":"+kwargs['string'])
        print("baseklass.describe2:"+self.bval+":"+kwargs['string2'])
        kwargs['string2'] = kwargs['string3']
        print("baseklass.describe2:"+self.bval+":"+kwargs['string2'])

class klass(baseklass):
    
    def __init__(self,val,bval):
        baseklass.__init__(self,bval)
        self.val = val

    def describe(self):
        super(klass,self).describe(10)
        super(klass,self).describe2(string='somestring', string2='anystring', string3='changestring')
        print("klass.describe:"+self.val)

    def describe2(self,**kwargs):
        print("klass.describe2:"+self.bval+":"+kwargs['string'])

k = klass("world","hello")
k.describe()
