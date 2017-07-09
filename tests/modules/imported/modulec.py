
#from . import submodules.submodulea
#from imported.submodules import submodulea
from submodules import submodulea
#import submodules.submodulea

def foo():
    print("imported.modulec.foo()")
    submodules.submodulea.foo()
