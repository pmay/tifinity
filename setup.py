# Copyright 2018 Peter May
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import codecs
import os
import re
from setuptools import setup, find_packages

# Project version approach from https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
# Version specified in tifinity.__init__.py
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='tifinity',
    version=find_version('tifinity', '__init__.py'),
    packages=find_packages(),  #['tifinity'],
    url='https://github.com/pmay/tifinity',
    license='Apache Licence 2.0',
    author='Peter May',
    author_email='Peter.May@bl.uk',
    description='Framework and helpful utilities for working with TIFFs',
    entry_points={
        'console_scripts': [
            'tifinity = tifinity.__main__:main'
        ]
    },
#     install_requires=[
#        "progressbar2>=3.6.2"
#     ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ]
)