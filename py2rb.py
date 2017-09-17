#! /usr/bin/env python

import sys
import os.path
from optparse import OptionParser
from py2rb import convert_py2rb

def main():
    parser = OptionParser(usage="%prog [options] filename [module filename [module filename [..]]]",
                          description="Python to Ruby compiler.")

    parser.add_option("--output",
                      action="store",
                      dest="output",
                      help="write output to OUTPUT")

    parser.add_option("--include-require",
                      action="store_true",
                      dest="include_require",
                      default=False,
                      help="require py-builtins.rb library in the output")

    parser.add_option("--include-builtins",
                      action="store_true",
                      dest="include_builtins",
                      default=False,
                      help="include py-builtins.rb library in the output")

    parser.add_option("--base-path",
                      action="store",
                      dest="base_path",
                      default=False,
                      help="set default module target path")

    parser.add_option("--base-path-count",
                      action="store",
                      dest="base_path_count",
                      default=0,
                      help="set default module target path nest count")

    options, args = parser.parse_args()
    if len(args) != 0:
        filename = args[0]
        subfilenames = args[1:]

        if options.output:
            output = open(options.output, "w")
        else:
            output = sys.stdout

        if options.include_require:
            if os.path.dirname(__file__):
                require = open(os.path.join(os.path.dirname(__file__),
                    "py-builtins-require.rb")).read()
                using = open(os.path.join(os.path.dirname(__file__),
                    "py-builtins-using.rb")).read()
            else:
                require = open("py-builtins-require.rb").read()
                using = open("py-builtins-using.rb").read()
            output.write(require)
            output.write(using)

        if options.include_builtins:
            if os.path.dirname(__file__):
                builtins = open(os.path.join(os.path.dirname(__file__),
                    "py-builtins.rb")).read()
                using = open(os.path.join(os.path.dirname(__file__),
                    "py-builtins-using.rb")).read()
            else:
                builtins = open("py-builtins.rb").read()
                using = open("py-builtins-using.rb").read()
            output.write(builtins)
            output.write(using)

        mods = []
        mod_paths = {}
        for f in subfilenames:
            rel_path = os.path.relpath(f, os.path.dirname(filename))
            name_path, ext = os.path.splitext(rel_path)
            mod_paths[f] = name_path
            mods.append(open(f).read()) #unsafe for large files!
        s = open(filename).read() #unsafe for large files!
        name_path = ''
        if options.base_path:
            rel_path = os.path.relpath(filename, options.base_path)
            name_path, ext = os.path.splitext(rel_path)
        base_path_count = int(options.base_path_count)
        output.write(convert_py2rb(s, name_path, base_path_count, mods, mod_paths))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
