"""A module handling a lot of the common string operations we will be using."""


# ============================================================================
# String Utilities
def normalize_string(input_string: str,
                     strip_spaces: bool = True,
                     remove_wildcards: bool = False,
                     lower: bool = False):
    """
    Operate on a string to normalize them into a common format.

    For a given string strip leading and trailing blank spaces and
    ensure all slashes are forward slashes

    Args:
        input_string (str): The string to be normalized.
        strip_spaces (bool, optional): A flag determining if we should strip
             spaces.
        remove_wildcards (bool, optional): A flag determining if we should
            strip wildcards.
        lower (bool, optional): A flag determining if we should switch the
            string to lowercase.

    Returns:
        str: the normalized string.

    """
    return _fix_string(input_string, strip_spaces, remove_wildcards, lower)


def normalize_strings(string_list: list,
                      strip_spaces: bool = True,
                      remove_wildcards: bool = False,
                      lower: bool = False):
    """
    Operate on each string within a list normalizing them into a common format.

    For each of the strings in a list, strip leading and trailing blank spaces
        and ensure all slashes are forward slashes

    Args:
        string_list (str): A list of strings to be normalized.
        strip_spaces (bool, optional): A flag determining if we should
            strip spaces.
        remove_wildcards (bool, optional): A flag determining if we should
            strip wildcards.
        lower (bool, optional): A flag determining if we should switch the
            string to lowercase.

    Returns:
        list: A new list with all strings normalized.

    """
    fixed_strings_list = []

    for i in string_list:
        fixed_strings_list.append(
            normalize_string(
                i,
                strip_spaces,
                remove_wildcards,
                lower)
            )

    return fixed_strings_list


def _fix_string(input_string: str,
                strip_spaces: bool = True,
                remove_wildcards: bool = False,
                lower: bool = False):
    """
    Fix the following: slashes, case, leading and trailing blank spaces.

    Args:
        input_string (str): The string to be normalized.
        strip_spaces (bool, optional): A flag determining if we should strip
            spaces.
        remove_wildcards (bool, optional): A flag determining if we should
            strip wildcards.
        lower (bool, optional): A flag determining if we should switch the
            string to lowercase.

    Returns:
        string: the fixed up string.

    """
    temp_str = input_string

    if strip_spaces:
        # remove whitespaces from begining and end of string, just in case
        temp_str = input_string.strip(' ')

    if remove_wildcards:
        temp_str = temp_str.strip('*')
    # lower case to avoid problems while comparing
    # temp_str = temp_str.lower()

    # make sure all slashes are correct, just in case
    temp_str = temp_str.replace('//', '/')
    temp_str = temp_str.replace('\\\\', '/')
    temp_str = temp_str.replace('\\', '/')

    if lower:
        temp_str = temp_str.lower()

    return temp_str


def _fix_strings(string_list: list):
    """
    Fix in a list: slashes, case, leading and trailing blank spaces.

    Args:
        string_list (list): Description

    Returns:
        list: A new list of fixed up strings.

    """
    fixed_strings_list = []

    for i in string_list:
        fixed_strings_list.append(_fix_string(i))

    return fixed_strings_list


def friendly_list_to_str(some_list: list):
    """
    Fixup arrays into pretty indented lists.

    Grab an array or list of strings and makes it into a nice string to
    be printed out by the logger.

    Args:
        some_list (list): a list containing strings.

    Returns:
        string: A new string representing an indented array.

    """
    temp_string = '\n['
    for i in some_list:
        temp_string += f'\n\t\"{i}\"'

    temp_string += '\n]'
    return temp_string


def ensure_path_compliance(path: str):
    """
    Ensure paths are quoted if they have spaces for compliance.

    Args:
        path (str): The path we want to validate.

    Returns:
        str: compliant path.

    """
    if path.startswith("\"") and path.endswith("\""):
        return path

    if ' ' in path:
        return f"\"{path.rstrip()}\""

    return path


def convert_to_regex_entries(list_input: list):
    """
    Convert a list of strings to a list of regex compliant entries.

    Notes:
        - ** are special git ignore wildcards that translates to .+ in regex.
        - all single wildcards are converted to .+ (greedy capture everything)

    Args:
        list_input (list): The raw list of strings to convert to regex
            compliant entries.

    Returns:
        list: A list of strings converted to regex compliant strings.

    """
    converted_list = []
    for item in list_input:
        converted_list.append(convert_to_regex_entry(item))
    return converted_list


def convert_to_regex_entry(string_input: str):
    """
    Convert a single string to regex format.

    Args:
        string_input (str): A single string that will be converted to be regex
            compliant.

    Returns:
        str: A regex compliant string.

    """
    result = string_input

    # SPECIAL CASE: Checking if we are actually trying to ignore an extension.
    #   Force check at the end of the string. If we don't do this, then we
    #   end up ignoring the wrong things.

    if result.startswith("*") and not result.endswith("*"):
        result = result + '$'

    # SPECIAL CASE: Periods are any character in regex. But python doesn't
    #    push the string as single backlash for it to be correctly escaped.
    #    Instead it uses '\\.' which translates to matching a backlash +
    #     any character

    if "." in result:
        # Captures wildcards anywhere in the string
        result = result.replace(".", "[.]")

    # SPECIAL CASE: Translating the wildcard. A wildcard matches everything
    #   in git which is the equivalent of the greedy capture all character
    #   quantifier .*

    if "*" in result:
        # Captures wildcards anywhere in the string
        result = result.replace("*", ".*")

    return result

# ============================================================================
