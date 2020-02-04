Changelog
=========

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[0.3.0] - 2020-02-04
------------

Added
~~~~~
* ICC Parser, handling and printing
* Additional tag names for XMP, IPTC, Photoshop, EXIF, and ICC Profile

Changed
~~~~~~~
* Improved tag printing for long-length tag values

Fixed
~~~~~
* Fixed a bug in the Tiff parser when reading a tag type that is outside the TIFF v6 spec range
* ASCII tags now print out as characters


[0.2.1] - 2018-05-18
--------------------

Added
~~~~~
* Batch script and spec files for building windows executables with PyInstaller

Changed
~~~~~~~
* Modified approach to import Tifinity modules to support running as an exe

[0.2.0] - 2018-05-15
--------------------

Added
~~~~~
* Unit tests for Checksum module
* Test resources (hand crafted example TIFF files)
* read_float and read_double methods in TIFF parser
* Module to compare two tiffs (currently only via MD5 checksum)

Changed
~~~~~~~
* Updated README
* Checksum module process_cli method now returns checksum output (as well as printing to console)

Fixed
~~~~~
* Added numpy dependency to setup.py
* Improved read handling of TIFFs with tag types beyond those allowed in TIFF v6 specification
* Corrected TiffFileHandler byteorder support to enable big-endian TIFF file reading


[0.1.0] - 2018-04-13
--------------------

Added
~~~~~
* Initial version of code
* Added new modules:
** RGB 72bpi TIFF migration utility
** TIFF IFD console display utility
** Checksum (full and image data) calculation utility
* Pip packaging
* Readme and Changelog