#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

import os

from setuptools import setup, find_packages

from suqc.paths import Paths as pa
from suqc import __version__

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------

with open(pa.path_package_indicator_file(), "w") as file:
    file.write(f"version={__version__}")


assert os.path.exists(pa.path_package_indicator_file())

setup(
    name="suqc",
    version=__version__,
    packages=find_packages(),
    data_files=[('suqc', ["suqc/PACKAGE.txt"])]
)

os.remove(pa.path_package_indicator_file())
assert not os.path.exists(pa.path_package_indicator_file())