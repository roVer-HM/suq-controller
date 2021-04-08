#!/usr/bin/env python3

import os
import importlib.util

from setuptools import find_packages, setup

from suqc.configuration import SuqcConfig

def read_suqc_version():
    """This reads the version from suqc/_version.py without importing parts of
    suqc (which would require some of the dependencies already installed)."""
    # code parts taken from here https://stackoverflow.com/a/67692

    path2setup = os.path.dirname(__file__)
    version_file = os.path.join(path2setup, "suqc", "_version.py")
    version_file = os.path.abspath(version_file)

    spec = importlib.util.spec_from_file_location("version", version_file)
    version = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version)
    return version.Version.v_short


# To generate a new requirements.txt file run in console (install vis 'pip3 install pipreqs'):
# pipreqs --use-local --force /home/daniel/REPOS/suq-controller


with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

# Writes a file that gives information about the version such that "suqc.__version__" provides the current version,
# which is a convention in Python:
with open(SuqcConfig.path_package_indicator_file(), "w") as file:
    file.write(f"version={read_suqc_version()}")

assert os.path.exists(SuqcConfig.path_package_indicator_file())

setup(
    name="suqc",
    version=read_suqc_version(),
    license="LGPL",
    url="www.vadere.org",
    packages=find_packages(),
    install_requires=requirements,
    data_files=[("suqc", ["suqc/PACKAGE.txt"])],
)

os.remove(SuqcConfig.path_package_indicator_file())
assert not os.path.exists(SuqcConfig.path_package_indicator_file())
