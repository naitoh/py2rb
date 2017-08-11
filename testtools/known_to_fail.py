"""lists all the tests that are known to fail"""
KNOWN_TO_FAIL = [
    "tests/basic/nestedclass.py",
    "tests/basic/listcomp2.py",
    "tests/basic/del_local.py",
    "tests/basic/valueerror.py",
    "tests/basic/del_attr.py",
    "tests/basic/del_global.py",
    "tests/basic/generator.py",
    "tests/basic/class3.py",  # Can't call class()
    "tests/basic/class4.py",  # Can't call class()
    "tests/basic/class5.py",  # Can't call class()
    "tests/basic/class6.py",  # Can't call class()
    "tests/basic/default.py", # Can't call local valiable in arguments.
    "tests/basic/hasattr.py",
    "tests/basic/oo_super.py", # Multiple inheritance can not be supported

    "tests/functions/sort_cmp.py",
    "tests/functions/sort23.py",

    "tests/errors/decorator.py",

    "tests/lists/reduce.py",
    "tests/lists/subclass.py",

    "tests/libraries/xmlwriter.py",

    "tests/modules/classname.py",
    "tests/modules/from_import.py",
    "tests/modules/import.py",
    "tests/modules/import_alias.py",
    "tests/modules/import_class.py",
    "tests/modules/import_diamond.py",
    "tests/modules/import_global.py",
    "tests/modules/import_multi.py",
    "tests/modules/module_name.py",
    "tests/modules/rng.py",

    "tests/strings/other_strings.py",    # not support
    "tests/strings/replace2.py",         # not support 3rd argument.
    "tests/strings/string_format_efg.py",
    "tests/strings/string_format_o.py", # not support
    "tests/strings/string_format_x.py", # not support
    ]


