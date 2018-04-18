========
Tifinity
========

A framework and helpful utilities for working with TIFF files.

|license|

Installation
============

::

    pip install tifinity

How to use
==========

Base usage: ``tifinity [-h] [-v] {module} [module-options]``

module selection:
  module            One of the modules below

optional arguments:
  -h, --help        Show the help message and exit
  -v, --version     Provide the version of this application

Tifinity is a framework encompassing a TIFF parser and a number of processing modules. Modules operate on TIFF files to
delivery desired functionality, such as displaying tags or migrating the contents of the files. New modules can easily
be created and added to the framework.

The base tifinity command (without any module specified) simply outputs the application's main help or the application's
version - not hugely interesting!

To be of use for processing TIFFs, a module needs to be specified.

Modules
-------

Available modules are:

migrate_rgb72
^^^^^^^^^^^^^
Migrates RGB TIFF images that are encoded as 24 bits-per-channel (i.e. 72 bits per pixel) to 36 bits-per-channel (96 bpi).

Usage: ``tifinity migrate_rgb72 [-h] [-o OUTPUT] path [path...]``

positional arguments:
  path(s)            a TIFF file or folder(s) containing TIFF files to migrate

optional arguments:
  -h, --help        Show the help message and exit
  -o OUTPUT         CSV file to output statistics too

show_tags
^^^^^^^^^
Prints to console the IFD tags of the specified TIFF image.

Usage: ``tifinity show_tags [-h] file``

positional arguments:
  file              the TIFF file whose IFD tags to show

optional arguments:
  -h, --help        Show the help message and exit

checksum
^^^^^^^^
Calculates checksum values for the image data in each sub-image of the specified TIFF, as well as the full file.

Usage: ``tifinity checksum [-h] [-a {md5,sha256,sha512,sha3_256,sha3_512}] [--json] file``

positional arguments:
  file              the TIFF file to generate checksum values for

optional arguments:
  -a                the checksum algorithm to use
  --json            JSON formatted output; otherwise just prints to terminal
  -h, --help        Show the help message and exit

Development
===========

Tifinity's folder structure is as below:

::

    tifinity
    |--- actions
    |--- modules
    |--- parser
    |--- scripts
    |--- __main__.py

Modules are contained in the *modules* folder, supported by reusable cross-module scripted functions in the *actions*
folder, and helper functions in the *scripts* folder.

The main TIFF parser is self contained in the *parser* folder.

Adding new Modules
------------------

An Abstract Base Module for all Modules is defined in `modules/__init__.py <http://www.github.com/tifinity/tifinity/modules/__init__.py>`_.

This defines two abstract methods which all subclassing modules must implement:

add_subparser(mainparser):
  This adds a argparse subparser to the mainparser obtained from __main__.py.
  The subparser should define any command line arguments pertinent to it. It must also set a default 'func' key pointing
  to the process_cli function.

  For example::

    def add_subparser(self, mainparser):
        m_parser = mainparser.add_parser(self.cli_name)
        m_parser.set_defaults(func=self.process_cli)
        m_parser.add_argument("path", nargs="+", help="the TIFF file or folder(s) containing TIFFs to migrate.")
        m_parser.add_argument("-o", dest="output", help="the output folder to output the converted TIFF(s) to.")

process_cli(args):


License
=======

Released under `Apache version 2.0 license <LICENSE>`_.

Contribute
==========

1. `Fork the GitHub project <https://help.github.com/articles/fork-a-repo>`_
2. Change the code and push into the forked project
3. `Submit a pull request <https://help.github.com/articles/using-pull-requests>`_


.. |license| image:: https://img.shields.io/badge/license-Apache%20V2-blue.svg
   :target: https://github.com/pmay/tifinity/blob/master/LICENSE
   :alt: Apache V2