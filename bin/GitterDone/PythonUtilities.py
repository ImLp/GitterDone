"""
Python Utilities.

Handles python version verification and terminating gracefully.
"""
import logging
import sys


def verify_python_version():
    """Verify that the Python 3+ requirement has been met."""
    if sys.version_info[0] < 3:
        logging.error(f'This script requires Python 3 or greater,\
        \nThe detected version is Python {0}. Terminating Execution'.format(
            sys.version_info[0]))
        terminate(True)


def terminate(forced):
    """
    Stop execution.

    Args:
        forced (int): The code to use for the exit message.

    """
    if forced:
        logging.fatal('Terminating due to error.')
        sys.exit(-1)
    else:
        logging.info('Completed successfully.')
        sys.exit(0)


def terminate_with_message(message: str):
    """
    Stop Execution while delivering an error message to screen.

    Args:
        message (str): The log message to display.

    """
    logging.fatal(message)
    terminate(True)
