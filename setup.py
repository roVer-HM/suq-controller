#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from setuptools import setup, find_packages

from paths_and_filenames import *

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

VERSION = "0.1"
with open(PACKAGE_FILE_PATH, "w") as file:
    file.write(f"version={VERSION}")

setup(  # TODO include the Package file into the installation!
    name="suqc",
    version=VERSION,
    packages=find_packages(),
    data_files=[('suqc', ["suqc/PACKAGE.txt"])]
)


