import argparse
import importlib
import pkgutil
import sys

from tifinity import __version__


def load_modules(package):
    """ Imports all valid modules in the specified package, with support for PyInstaller.
        See: https://github.com/pyinstaller/pyinstaller/issues/1905
        Adjusted from: https://github.com/webcomics/dosage/blob/master/dosagelib/loader.py
        """
    mod = importlib.import_module(package, __name__)
    prefix = mod.__name__ + "."
    modules = [m[1] for m in pkgutil.iter_modules(mod.__path__, prefix)]

    # special handling for PyInstaller
    importers = map(pkgutil.get_importer, mod.__path__)
    toc = set()
    for i in importers:
        if hasattr(i, 'toc'):
            toc |= i.toc
    for elm in toc:
        if elm.startswith(prefix):
            modules.append(elm)

    for name in modules:
        try:
            yield importlib.import_module(name)
        except ImportError as msg:
            print("Could not load module " + name + ":" + msg)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    # Process CLI arguments #
    ap = argparse.ArgumentParser(prog="Tifinity",
                                 description="Helpful TIFF analysis and action tools")

    moduleparsers = ap.add_subparsers(title='Available Modules', dest='module')

    # Set up each module
    for module in load_modules("tifinity.modules"):
        m = module.module               # initiate the module
        m.add_subparser(moduleparsers)  # add sub-parser to this argparse handler

    # ap.add_argument("-s", "--silent", dest="silent", action="store_true",
    #                help="turn off command line output")
    ap.add_argument("-v", "--version", action="version", version='%(prog)s v' + __version__,
                    help="display program version")
    arguments = ap.parse_args()

    # Now try to call the appropriate sub-parser handling function, or print the help if not
    try:
        arguments.func(arguments)
    except AttributeError:
        ap.print_help()


if __name__ == '__main__':
    main()
