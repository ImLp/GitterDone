"""A module focused on path & file handling operations."""
import glob
import os
import re
import logging
import sys

from . import git_utility
from . import string_utility


# ============================================================================
# Path utilties.
def expand_path(string):
    """
    Expand a path with a wildcard (*) suffix, if possible.

    Returns a list of paths, possibly empty.

    Args:
        string (string): The path to be expanded.

    Returns:
        string: A string with the expanded path.

    """
    # remove whitespaces from begining and end of string, just in case
    path = string.strip(' ')

    # prepare path for the glob function
    if path:
        if path[0] == '/':
            path = "." + path
        else:
            path = "./" + path

    # search all files and directories that match
    temp_list = glob.glob(path)
    return temp_list


def generate_wishlist_filemap(wish_list):
    """
    Walk through the GIT_FILE_WISHLIST generating the correct path format.

    Args:
        wish_list (list): the list of relative paths to expand into the list of
            files to track.

    Returns:
        dict: object containing all the information about the path.

    """
    file_map = {}

    # for each path in the wish list
    for path in sorted(wish_list):
        # split the path into smaller strings
        split_path = path.split("/")

        # if the first element is an empty string, get rid of it
        if not split_path[0].strip(' '):
            del split_path[0]

        # this string will grow as the path grows
        temp_path = ""

        # for each level of the path
        for i, item in enumerate(split_path):

            is_leaf = False

            if len(split_path) == 1:
                # it's a file in the root
                temp_path = item
            elif i > 0:
                # it's not a file in the root, let's add a slash (/)
                if sys.platform == 'win32':
                    temp_path += os.altsep + item
                else:
                    temp_path += os.sep + item
            else:
                temp_path += item

            # check if this is the leaf
            if i == len(split_path) - 1:
                is_leaf = True

            # store the path into the dictionary
            key = temp_path.lower()
            file_map[key] = git_utility.Node(temp_path, is_leaf)

    return file_map


def get_files_from_directory(directory):
    """
    Get a list with the path of all the files in a directory.

    Args:
        directory (str): The path to the directory.

    Returns:
        list: List containing all the files in a directory.

    """
    file_list = []
    for root, dirs, files in os.walk(directory):  # pylint:disable=W0612
        for name in files:
            file_list.append(
                string_utility.normalize_string(os.path.join(root, name))
                )
    return file_list


def _get_normalized_files_in_directory(directory: str):
    entries = os.listdir(directory)

    files = [f.lower() for f in entries if os.path.isfile(
        os.path.join(directory, f))]

    files = string_utility.normalize_strings(files, lower=True)
    logging.debug("Files found under '%s' are: %s",
                  directory,
                  string_utility.friendly_list_to_str(files))
    return files


def _get_normalized_directories_in_directory(directory: str):
    entries = os.listdir(directory)

    directories = [d for d in entries if os.path.isdir(os.path.join(
        directory, d))]

    directories = string_utility.normalize_strings(directories, lower=True)
    logging.debug("Directories found under '%s' are: %s",
                  directory,
                  string_utility.friendly_list_to_str(directories))
    return directories


def _get_normalized_combined_path(root: str, suffix: str):
    return string_utility.normalize_string(os.path.join(root, suffix))


def _get_combined_filtered_list(
        list_1: list,
        list_2: list,
        lower: bool = False):

    if lower:
        return [x for x in list_1 if x.lower() not in list_2]
    return [x for x in list_1 if x not in list_2]


def _insert_items_in_list(
        raw_list: list,
        root: str,
        exclude_list: list,
        output_list: list):

    for file in raw_list:
        path = _get_normalized_combined_path(root, file)
        output_list = _insert_item_in_list(path[2:], exclude_list, output_list)
    return output_list


def _insert_item_in_list(
        item: str,
        exclude_list: list,
        output_list: list):

    if item not in exclude_list and item not in output_list:
        logging.debug("Adding the following exclude list '%s'", item)
        output_list.append(item)
    return output_list


def _build_pattern_list(root_directory: str,
                        desired: list):
    desired_pattern = []
    for entry in desired:
        if not root_directory == ".":
            prefix_to_strip = root_directory.lower()[2:]
            if not prefix_to_strip == entry:
                if sys.platform == 'win32':
                    splitting_regex = prefix_to_strip + os.altsep
                else:
                    splitting_regex = prefix_to_strip + os.sep
                raw_list = entry.strip("*").split(splitting_regex)
                desired_pattern.extend(list(filter(None, raw_list)))
        else:
            desired_pattern.append(entry)
    return desired_pattern


# pylint: disable=too-many-arguments
def _cull_files(root_directory: str,
                raw_files: list,
                desired_patterns: list,
                exclude_list: list,
                ignore_regex: list,
                should_ignore_files: bool = False):
    files_to_ignore = []
    filtered_files = []
    undesired_files = list(set(raw_files)-set(desired_patterns))
    for file in undesired_files:
        found_match = False
        for entry in ignore_regex:
            match = re.search(entry, file, re.I)
            if match:
                found_match = True
                logging.debug("Matched %s with %s. Ignoring this file",
                              file,
                              entry)
                filtered_files.append(file.lower())

        if not found_match:
            logging.debug("Found a Desired File: %s", file)

    undesired_files = list(set(undesired_files)-set(filtered_files))

    if not desired_patterns:
        undesired_files = []
    if should_ignore_files:
        undesired_files = list(set(undesired_files)-set(filtered_files))

    if undesired_files:
        logging.debug("Ignoring the following files found under '%s': %s",
                      root_directory,
                      string_utility.friendly_list_to_str(undesired_files))

    files_to_ignore = _insert_items_in_list(undesired_files,
                                            root_directory,
                                            exclude_list,
                                            files_to_ignore)

    return files_to_ignore
# pylint: enable=too-many-arguments


# pylint: disable=too-many-locals
def recursely_get_ignored(root_directory: str,
                          results: list,
                          desired: list,
                          ignore_regex: list):
    """
    Recursively walk a directory tree and return the list of objects to ignore.

    Args:
        root_directory (str): The path to start recursing from.
        results (list): List of paths mapping to directories found under the
            root directory.
        ignore_regex (list, optional): A list of regex strings to run against
            the entries such so we exclude matches.

    Returns:
        list: List of directories found under the root directory.

    """
    logging.info(("Recursively extracting all ignored folders "
                  "in the tree starting from '%s'"),
                 root_directory)

    if not os.path.isdir(root_directory):
        logging.error("The path \'%s\' is not a directory.")

    raw_files = _get_normalized_files_in_directory(root_directory)
    raw_directories = _get_normalized_directories_in_directory(root_directory)

    files_to_ignore = []
    directories_to_ignore = []
    desired_entries = []
    regex_list = []
    desired_pattern = _build_pattern_list(root_directory, desired)

    logging.debug(("Checking the entries found under '%s'"
                   " against any found on: %s"),
                  root_directory,
                  string_utility.friendly_list_to_str(desired_pattern))

    for entry in desired_pattern:
        regex_list.append(re.compile(entry, re.I))

    # Cull out the undesired directories.
    recursion_results = []
    for folder in raw_directories:
        found_match = False
        for entry in ignore_regex:
            match = re.search(entry, folder, re.I)
            if match:
                found_match = True
                logging.debug("Matched %s with %s. Ignoring this directory",
                              folder,
                              entry)
        if not found_match:
            # reduce the list filtering ones matching this directory
            regex = re.compile(folder, re.I)
            matches = list(filter(regex.search, desired))
            path = string_utility.normalize_string(
                os.path.join(root_directory, folder)
                )

            # Continue going down the rabbit hole.
            if matches:
                recursion_results = recursely_get_ignored(path,
                                                          results,
                                                          matches,
                                                          ignore_regex)
            elif len(desired) == 1:
                desired_entries.append(folder)

        results.extend(
            _get_combined_filtered_list(recursion_results, results, True)
            )

    undesired_dirs = (
        sorted(
            list(
                set({x.lower() for x in raw_directories} -
                    set(desired_pattern) -
                    set(desired_entries))))
        )

    if undesired_dirs:
        logging.debug("Ignoring the following directories found @ '%s': %s",
                      root_directory,
                      string_utility.friendly_list_to_str(undesired_dirs))

    directories_to_ignore = _insert_items_in_list(undesired_dirs,
                                                  root_directory,
                                                  results,
                                                  directories_to_ignore)

    # Cull out the undesired files.
    should_ignore_files = any([s for s in results if root_directory[2:] in s])
    files_to_ignore = _cull_files(root_directory,
                                  raw_files,
                                  desired_pattern,
                                  results,
                                  ignore_regex,
                                  should_ignore_files)
    # if the current folder is the last on the desired group and there are
    # no more folders to walk under. Then we may want to add the files here
    # as the desired entry includes all of it.

    results += [x for x in files_to_ignore if x.lower() not in results]
    results += [x for x in directories_to_ignore if x.lower() not in results]
    return results

# pylint: enable=too-many-locals
# ============================================================================
