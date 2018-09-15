#!/usr/bin/env python3

# TODO: """ << INCLUDE DOCSTRING (one-line or multi-line) >> """

# include imports after here:
import os
import sys
import shutil
import subprocess

import suqc.paths

import pandas as pd
from typing import Union

# --------------------------------------------------
# people who contributed code
__authors__ = "Daniel Lehmberg"
# people who made suggestions or reported bugs but didn't contribute code
__credits__ = ["n/a"]
# --------------------------------------------------


def get_current_suqc_state():
    # message only for developer, -- if the installed package is running
    if not suqc.paths.Paths.is_package_paths():
        GIT_COMMIT_HASH = subprocess.check_output(["git", "rev-parse", "HEAD"])
        GIT_COMMIT_HASH = GIT_COMMIT_HASH.decode().strip()

        uncommited_changes = subprocess.check_output(["git", "status", "--porcelain"])
        uncommited_changes = uncommited_changes.decode()  # is returned as a byte sequence -> decode to string

        if uncommited_changes:
            print("WARNING: THERE ARE UNCOMMITED CHANGED IN THE REPO")
            print("In order to have a reproducible scenario run you should check if untracked changes in the following "
                  "files should be commited before: \n")
            print(uncommited_changes)

        return {"git_hash": GIT_COMMIT_HASH, "umcommited_changes": uncommited_changes}
    else:
        return {"suqc_version": suqc.__version__}


def cast_series_if_possible(data: Union[pd.DataFrame, pd.Series]):
    if isinstance(data, pd.Series):
        return data  # already Series, nothing to do

    if isinstance(data, pd.DataFrame) and data.shape[1] == 1:
        return data.iloc[:, 0]
    else:
        return data  # not a Series, remains a DataFrame


def create_folder(path, delete_if_exists=True):
    if delete_if_exists and os.path.exists(path):
        remove_folder(path)
    os.mkdir(path)


def remove_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def user_query_yes_no(question: str, default=None) -> bool:
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """

    # source: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input

    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        sys.stdout.flush()
        choice = input().lower()
        sys.stdout.write("\n")
        sys.stdout.flush()

        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' (or 'y' or 'n').")


def user_query_numbered_list(elements: list):

    max_choice = len(elements)-1
    print("Choose an option of the following list:")

    for i, txt in enumerate(elements):
        print(f"{i} \t {txt}")

    while True:
        print(f"Type in a number between 0 and {max_choice}")
        choice = input().lower()
        try:
            choice = int(choice)
            if 0 <= choice <= max_choice:
                return elements[choice]
        except ValueError:
            print("The number has to be an integer.")

