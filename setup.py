#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

from setuptools import setup, find_packages

from suqc.paths import *

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

VERSION = "0.1"
with open(PATH_PACKAGE_FILE, "w") as file:
    file.write(f"version={VERSION}")


assert os.path.exists(PATH_PACKAGE_FILE)

setup(
    name="suqc",
    version=VERSION,
    packages=find_packages(),
    data_files=[('suqc', ["suqc/PACKAGE.txt"])]
)

os.remove(PATH_PACKAGE_FILE)
assert not os.path.exists(PATH_PACKAGE_FILE)