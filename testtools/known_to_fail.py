"""lists all the tests that are known to fail"""
KNOWN_TO_FAIL = [
    "tests/basic/nestedclass.py",
    "tests/basic/listcomp2.py",
    "tests/basic/del_local.py",
    "tests/basic/valueerror.py",
    "tests/basic/del_global.py",
    "tests/basic/generator.py",
    "tests/basic/default.py",    # Can't call local valiable in arguments.
    "tests/basic/for_in2.py",    # Can't support dict (not use items()/keys()/values()) case.
    "tests/basic/hasattr2.py",
    "tests/basic/oo_super.py",   # Multiple inheritance can not be supported
    "tests/basic/oo_diamond.py", # Multiple inheritance can not be supported
    "tests/basic/oo_static_inherit2.py", # A class method of the lowercase name class is unsupported.
    "tests/basic/vars.py",       # Can't match variable scope
    "tests/basic/vars2.py",      # Can't match variable scope
    "tests/basic/yield.py",      # Difficult

    "tests/functions/sort_cmp.py",
    "tests/functions/sort23.py",

    "tests/decorator/class.py",
    "tests/decorator/decorator.py",

    "tests/lists/reduce.py",

    "tests/libraries/xmlwriter.py",

    "tests/modules/import_diamond.py",
    "tests/modules/module_name.py",
    "tests/modules/rng.py",

    "tests/strings/other_strings.py",    # not support
    "tests/strings/replace2.py",         # not support 3rd argument.
    "tests/strings/string_format_efg.py",
    "tests/strings/string_format_o.py", # not support
    "tests/strings/string_format_x.py", # not support

    "tests/numpy/arg_max_min.py",       # Not Compatible with axis case
    ]


