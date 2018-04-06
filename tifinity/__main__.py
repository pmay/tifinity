import argparse
import importlib
import os
import sys

from tifinity import __version__

moduledir = "tifinity/modules"


def load_modules():
    modules = []
    possiblemodules = next(os.walk(moduledir))[2]   # os.walk returns (dirpath, dirnames, filenames)
    for i in possiblemodules:
        if i == '__init__.py':
            continue
        modules.append(importlib.import_module('.'+i[:-3], package='tifinity.modules'))
    return modules


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    modules = load_modules()

    # Process CLI arguments #
    ap = argparse.ArgumentParser(prog="Tifinity",
                                 description="Helpful TIFF analysis and action tools")

    moduleparsers = ap.add_subparsers(title='Modules',
                                     description='Valid modules',
                                     dest='module')

    # Set up each module
    for module in modules:
        m = module.module               # initiate the module
        m.add_subparser(moduleparsers)  # add sub-parser to this argparse handler

    #ap.add_argument("-o", dest="output",
    #                help="CSV file to output statistics too")
    #ap.add_argument("-s", "--silent", dest="silent", action="store_true",
    #                help="turn off command line output")
    ap.add_argument("-v", "--version", action="version", version='%(prog)s v' + __version__,
                    help="display program version")
    arguments = ap.parse_args()
    arguments.func(arguments)

if __name__=='__main__':
    main()
