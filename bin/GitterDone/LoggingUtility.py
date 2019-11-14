"""
Logging Utility.

This utility's responsibility is to set up the logging for the script.
"""
import datetime
import logging
import os
import sys


def get_logger_output_path(logger_output_dir: str,
                           use_temp_dir: bool = True):
    """
    Get the logger outputh path required by GitterDone.

    Returns:
        str: The absolute path to the logger output directory.
    Args:
        logger_output_dir (str): path to the output directory.

    """
    output_path = logger_output_dir
    if use_temp_dir:
        if sys.platform == 'win32':
            logging.debug('Windows System: Temp Key == \"TEMP\"')
            environ_key = "TEMP"
        else:
            logging.debug('OSX System: Temp Key == \"TMPDIR\"')
            environ_key = "TMPDIR"
        logging.debug('Attempting to retrive local user temp path.')
        output_path = os.environ[environ_key] + os.sep + logger_output_dir
    if not os.path.isdir(output_path):
        generate_new_logger_output_dir(output_path)

    return output_path


def generate_new_logger_output_dir(desired_path: str):
    """
    Generate a new logger output directory at the given path.

    Args:
        desired_path (str): Absolute path to the directory to be generated.

    """
    logging.debug('Adding new directory at: %s', desired_path)
    os.makedirs(desired_path)


def set_log_level(desired_log_level: str, log_to_file: bool,
                  log_output_path: str, log_output_filename: str):
    """
    Set the desired logging level for the runtime output.

    Args:
        desired_log_level (str): The default desired log level.
        log_to_file (bool): should we log results to a file?
        log_output_path (str): Where to output the log file to.
        log_output_filename (str): What output log filename to use.

    """
    # First lets handle setting up the Log Level correctly.
    log_level = logging.INFO

    if desired_log_level == 'INFO':
        log_level = logging.INFO
    elif desired_log_level == 'DEBUG':
        log_level = logging.DEBUG
    elif desired_log_level == 'WARNING':
        log_level = logging.WARNING
    elif desired_log_level == 'ERROR':
        log_level = logging.ERROR

    root_logger = logging.getLogger('')

    # clear handles that logging creates in obscure logging.basicConfig() call.
    root_logger.handlers = []
    root_logger.setLevel(logging.DEBUG)

    # Set up the Console Logger to the default level.
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s: %(message)s\n',
        datefmt='%Y-%m-%d %H:%M:%S')
    console_logger = logging.StreamHandler()
    console_logger.setLevel(log_level)
    console_logger.setFormatter(console_formatter)
    console_logger.propagate = False

    # NOTE:Earliest we can start logging to console.
    root_logger.addHandler(console_logger)

    if log_to_file:
        # Set up the file logger in the user's temp folder.
        file_logger_output_path = log_output_path
        file_logger_output_name =\
            log_output_filename + '_{:%Y-%m-%d_%H-%M-%S}.txt'.format(
                datetime.datetime.now())
        file_logger_absolute_path =\
            file_logger_output_path + os.sep + file_logger_output_name
        file_logger = logging.FileHandler(file_logger_absolute_path)
        file_logger.setLevel(logging.DEBUG)
        file_formatter =\
            logging.Formatter(
                fmt=('%(asctime)s.%(msecs)03d - '
                     '%(name)s - %(levelname)s: %(message)s\n'),
                datefmt='%Y-%m-%d %H:%M:%S')
        file_logger.setFormatter(file_formatter)
        root_logger.addHandler(file_logger)
