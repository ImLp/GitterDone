"""A module handling the console interaction operations with the user."""
import sys
import logging


# ============================================================================
# User interaction Utilities
def console_prompt(message: str):
    """
    Console print message pipe.

    We use a custom print format to display messages to console.
    Makes it automation friendly as it separates it from the std.output.
    Note this relies on the print magic from python 3.+.

    Args:
        message (string): The string to print out to the console.

    """
    print(message, file=sys.stderr)


def request_user_console_input(message: str):
    """
    Prompt the user and wait for console input.

    Reads a single line of input. Refer to the python documentation regarding
        the input() handling.

    Args:
        message (str): the message to prompt to the user.

    Returns:
        str: The input value(s) received.

    """
    console_prompt(message)
    return input()


def request_user_input_with_choices(
        message: str,
        choices: str,
        true_condition: str,
        false_condition: str):
    """
    Prompt the user for input forcing them to a specific pair of responses.

    Args:
        message (str): The prompt message to display.
        choices (str): A string representation of the available choices
            separated by a '/'
        true_condition (str): The positive choice that must be entered by the
            user.
        false_condition (str): The negative choice that must be entered by the
            user.

    Returns:
        bool: True if the user input matches the truth condition.

    """
    handled = False
    while not handled:
        request_prompt_string = f"{message}. ({choices})"
        request = request_user_console_input(request_prompt_string)

        if request is true_condition:
            return True

        if request is false_condition:
            return False

        logging.error(
            "User Input: %s does not match possible choices: [%s, %s]",
            request,
            true_condition,
            false_condition)

        console_prompt(
            ("Unknown choice received. Please enter either \'%s\' or \'%s\'",
             true_condition,
             false_condition))
# ============================================================================
