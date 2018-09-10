#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os

from setuptools import setup, find_packages

from suqc.paths import Paths as pa

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

VERSION = "0.1"
with open(pa.path_package_indicator_file(), "w") as file:
    file.write(f"version={VERSION}")


assert os.path.exists(pa.path_package_indicator_file())

setup(
    name="suqc",
    version=VERSION,
    packages=find_packages(),
    data_files=[('suqc', ["suqc/PACKAGE.txt"])]
)

os.remove(pa.path_package_indicator_file())
assert not os.path.exists(pa.path_package_indicator_file())