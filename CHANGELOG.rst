Changelog
=========

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

[Unreleased]
------------

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