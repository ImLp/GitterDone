"""A module used to access all the project specific information."""

import logging
import sys

from . import ExternalProcessUtility as external_process
from . import StringUtilities as str_utility


# ============================================================================
# Project Utilities
def get_vfs_tool_path():
    """
    Get the path to the VFS executable command for smart syncing.

    Returns:
        str: The absolute path to the vfs.cmd tool.

    """
    path = get_tools_root_path() + '\\Bin\\vfs.cmd'
    return path


def get_p4vfs_tool_path():
    """
    Get the path to the a VFS executable for smart syncing p4 files.

    Returns:
        str: The absolute path to the p4vfs.exe tool.

    """
    # Uncomment below if your environment uses a VFS on top of P4 #
    # if sys.platform == 'win32':
    #     command = "where.exe p4vfs.exe"
    # else:
    #     command = "which p4vfs.exe"
    # successfull_command_call, \
    #     command_results = external_process.trigger_external_subprocess(
    #         command)

    # if successfull_command_call:
    #     logging.info("Found the location of the VFS tool at: %s",
    #                  command_results)
    #     return str_utility.ensure_path_compliance(command_results)

    # logging.error(("Could not locate VFS tool."
    #                " Defaulting to Non VFS System."))

    path = get_p4_tool_path()
    return path


def get_p4_tool_path():
    """
    Get the path to the SourceDepot executable for force syncing.

    Returns:
        str: The absolute path to the sd.exe.

    """
    if sys.platform == 'win32':
        command = "where.exe p4.exe"
    else:
        command = "which p4"
    successfull_command_call, \
        command_results = external_process.trigger_external_subprocess(
            command)

    if successfull_command_call:
        logging.info("Found the location of the P4 tool at: %s",
                     command_results)
        return str_utility.ensure_path_compliance(command_results)

    logging.error(("Could not locate P tool."
                   " Defaulting to root System."))
    return '.'


def get_tools_root_path():
    """
    Get the absolute path to the tools from a system's environment variable.

    Returns:
        str: The tools root absolute file path.

    """
    logging.debug('Attempting to deduce the tools root path.')
    # Uncomment below if system has specific tools location #
    # tools_root_path = os.environ['TOOLROOT']
    # if tools_root_path:
    #     logging.debug('Tool Root Path being used: %s', tools_root_path)
    #     return tools_root_path

    # logging.error('Could not deduce the tools root path.')
    return '.'


def get_project_root_path():
    """
    Get the absolute path to the project via  asystem's environment variable.

    Returns:
        str: The absolute path to the project root if found.

    """
    logging.debug('Attempting to deduce project root.')
    # Uncomment below if system has specific project system variable  #
    # project_root_path = os.environ['PROJECTROOT']
    # if project_root_path:
    #     logging.debug('Project Root assumed to be at: %s', project_root_path)
    #     return project_root_path

    # logging.error('Could not deduce project environment root.')
    return '.'

# ============================================================================
