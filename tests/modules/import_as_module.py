
from imported.modulea import *
import imported.moduleb as foo

modulea_fn()
foo.moduleb_fn()

ma = modulea_class()
print(ma.msg(1))

mb = foo.moduleb_class()
print(mb.msg(2))
