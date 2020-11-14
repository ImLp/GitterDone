"""
Git<->P4 command line automation interface script.

Automates the processes that allows us to follow lightweight branching
strategies between Git & P4 source control solutions.

Attributes:
    LOGGER_OUTPUT_DIR_NAME (str): Name of the output directory to log to.
    TITLE_PROMPT (str): Some ASCII Art to make things pretty.
    IGNORED_FILE_LIST (list): A list of file paths that should be ignored by
        the main source control when building the change lists
        if they show modifications.
    GIT_FILE_WISHLIST (list): A list of file paths containing the files and
        folders we actually want to track in git.
    GIT_FILE_IGNORE_LIST (list): A list of file paths containing the files and
        and folders we want to absolutely ignore in git.

"""
import logging
import os
import sys

import bin.GitterDone.config as config
import bin.GitterDone.git_utility as git
import bin.GitterDone.string_utility as str_utility
import bin.GitterDone.console_utility as console_utility
import bin.GitterDone.arg_parser_utility as arg_parser_utility
import bin.GitterDone.logging_utility as logging_utility
import bin.GitterDone.python_utility as python_utility
import bin.GitterDone.p4_utility as p4_utility

# ============================================================================
# Global Variables.

LOGGER_OUTPUT_DIR_NAME = 'GitterDoneLogs'
TITLE_PROMPT = "\
\n======================================================\
\n   _____ _ _   _            _____                   \
\n  / ____(_) | | |          |  __ \\                  \
\n | |  __ _| |_| |_ ___ _ __| |  | | ___  _ __   ___ \
\n | | |_ | | __| __/ _ \\ '__| |  | |/ _ \\| '_ \\ / _ \\\
\n | |__| | | |_| ||  __/ |  | |__| | (_) | | | |  __/\
\n  \\_____|_|\\__|\\__\\___|_|  |_____/ \\___/|_| |_|\\___|\
\n\
\n======================================================\
\n                                                    "

# ----------------------------------
# Definitions from config.py.

IGNORED_FILE_LIST = config.get_p4_ignore_wishlist()
GIT_FILE_WISHLIST = config.get_git_ignore_desired_path_wishlist()
GIT_FILE_IGNORE_LIST = config.get_git_ignore_ignored_path_wishlist()

# ============================================================================


# =========== SETUP & TEARDOWN
def _execute_user_process(args):
    """
    Execute the desired user process based on received arguments.

    Args:
        args(args): Argument object containing the system command line
        inputs obtained from the call to execute.

    Returns:
        None.

    """
    logging.debug(str_utility.friendly_list_to_str(sys.argv[1:]))

    # First handle if at least one operation is available.
    if (args.changelist is None and args.git is None
            and args.update_trunk is None):
        logging.error('No actionable arguments received.')
        python_utility.terminate(True)
        return

    if args.git:
        logging.info('Requested .gitignore update')
        git.generate_git_ignore(GIT_FILE_WISHLIST, GIT_FILE_IGNORE_LIST)

    if args.changelist is not None:
        logging.info('Performing a Perforce Operation.')
        p4_utility.execute_p4_offline_sync(
            args.changelist, args.include_trunk, args.ignored_branches)
    elif args.update_trunk is not None:
        p4_utility.execute_git_sync_with_p4(args.update_trunk, args.force,
                                            args.force_all)


# ============================================================================
# CUSTOM ARGUMENT PARSING FOR GitterDone.py

def _print_help():
    """
    Print the help information to the screen.

    Returns:
        string: The contents of the help message.

    """
    # TODO: Update Help Message.
    help_message = ""
    return help_message


def _add_parser_options(parser):
    if parser is None:
        python_utility.terminate_with_message(
            'Parser set up incorrectly. GitterDone interface non-functional.')

    # Trigger extracting all the local changes from a branch into a changelist.
    arg_parser_utility.add_parser_option(
        parser,
        '-cl',
        '--changelist',
        help=('Generate a new changelist with all files '
              'operations in a given Branch.'),
        type=str,
        nargs='?',
        action='store',
        const='',
        metavar='Branch')

    # Option to include master branch changes when generating p4 CL.
    arg_parser_utility.add_parser_option(
        parser,
        full_name='--include_trunk',
        help=('Flag to wheter include the trunk branch file '
              'operations on the changelist.'),
        action='store_true',
        default=None)

    # Trigger automatically generating a new .gitignore.
    arg_parser_utility.add_parser_option(
        parser,
        '-g',
        '--git',
        help='Regenerate the .gitignore file to be used by the repository.',
        action='store_true',
        default=None)

    # Update the master branch to either existing CL or new CL from P4.
    arg_parser_utility.add_parser_option(
        parser,
        '-u',
        '--update_trunk',
        help=('Updates the trunk branch to the latest available CL in'
              'SourceDepot. If a CL is given, updates to that CL instead.'),
        type=str,
        nargs='?',
        action='store',
        const='',
        metavar=('CL'))

    # Forces the P4 update operation so that files are clobbered.
    arg_parser_utility.add_parser_option(
        parser,
        '-f',
        '--force',
        help='Flag to force update operations.',
        action='store_true',
        default=None)

    # Forces each file in the tree to be clobbered.
    arg_parser_utility.add_parser_option(
        parser,
        '-fa',
        '--force_all',
        action='store_true',
        help=('Enable this flag to force sync all the '
              'tracked files. (POTENTIALLY SLOW)'),
        default=None)

    # Ignore certain branches when generating the CL for P4.
    arg_parser_utility.add_parser_option(
        parser, '-ig', '--ignored_branches', nargs='+', default=None)


# ============================================================================
# MAIN

if __name__ == '__main__':
    # Only run this if we are the main script being run.
    console_utility.console_prompt(TITLE_PROMPT)

    PARSER = arg_parser_utility.setup_parser(help_message=_print_help())
    _add_parser_options(PARSER)
    ARGS = PARSER.parse_args()

    logging_utility.set_log_level(
        desired_log_level=ARGS.loglevel,
        log_to_file=True,
        log_output_path=(
            logging_utility.get_logger_output_path(LOGGER_OUTPUT_DIR_NAME,
                                                   False)),
        log_output_filename=os.path.basename(__file__))

    python_utility.verify_python_version()
    _execute_user_process(ARGS)

    # Exit if we are done.
    python_utility.terminate(False)
