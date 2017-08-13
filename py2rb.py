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

    parser.add_option("--include-builtins",
                      action="store_true",
                      dest="include_builtins",
                      default=False,
                      help="include py-builtins.rb library in the output")

    options, args = parser.parse_args()
    if len(args) != 0:
        filename = args[0]
        subfilenames = args[1:]

        if options.output:
            output = open(options.output, "w")
        else:
            output = sys.stdout

        if options.include_builtins:
            if os.path.dirname(__file__):
                builtins = open(os.path.join(os.path.dirname(__file__),
                    "py-builtins.rb")).read()
            else:
                builtins = open("py-builtins.rb").read()
            output.write(builtins)

        mods = []
        mod_paths = {}
        for f in subfilenames:
            rel_path = os.path.relpath(f, os.path.dirname(filename))
            name_path, ext = os.path.splitext(rel_path)
            mod_paths[f] = name_path
            mods.append(open(f).read()) #unsafe for large files!
        s = open(filename).read() #unsafe for large files!
        output.write(convert_py2rb(s, mods, mod_paths))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
