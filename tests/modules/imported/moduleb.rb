def foo ()
    print('foo')
end
def moduleb_fn ()
    print('import_moduleb.moduleb_fn()')
end
class Moduleb_class
    def initialize()
        # pass
    end
    def msg(val)
        return ('moduleb_class:')+(val.to_s);
    end
end
