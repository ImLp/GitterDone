"""
P4<->Git command line automation interface script.

Attributes:
    IGNORED_P4_FILE_LIST (list): A list of file paths that should be ignored by
        P4 when building the change lists if they show modifications.
    GIT_FILE_WISHLIST (list): A list of file paths containing the files and
        folders we actually want to track in git.
    GIT_FILE_IGNORE_LIST (list): A list of file paths containing the files and
        folders we want to absolutely ignore in git.
    FORCED_SYNC_WISHLIST (list): A list of file paths containing
        the files and folders we want to forcefully sync via our automation.
    DEFAULT_REMOTE_NAME (str): A string representing the prefix of the git
        remote.

"""
import logging
import os

from . import config
from . import console_utility
from . import external_process_utility
from . import git_utility
from . import project_utility
from . import string_utility
# ============================================================================
# Global Variables.

# ----------------------------------
# Definitions from Config.py

IGNORED_P4_FILE_LIST = config.get_p4_ignore_wishlist()
GIT_FILE_WISHLIST = config.get_git_ignore_desired_path_wishlist()
GIT_FILE_IGNORE_LIST = config.get_git_ignore_ignored_path_wishlist()
FORCED_SYNC_WISHLIST = config.get_forced_sync_path_wishlist()
TRUNK_BRANCH_NAME = config.get_trunk_branch_name()


# ============================================================================
# P4 output handling functions

def _parse_edit_message(msg: str):
    """
    Parse the message received from P4 after an edit command.

    Args:
        msg (string): The output message to parse.

    Returns:
        string: A string representing the results:
            - "done" -- means that the command was successful
            - "add" -- means the file was not on the repository and should be
                added.
            - "unknown" -- means an error has occurred and should be handled
                by the caller.

    """
    # this covers "opened for edit" and "currently opened for edit" cases
    if msg.find('opened for edit') != -1:
        return 'done'

    if msg.find("can't edit (already opened for add)") != -1:
        return 'done'

    if msg.find('file(s) not on client') != -1:
        return 'add'

    return 'unknown'


def _parse_add_message(msg: str):
    """
    Parse the message received from P4 after an add command.

    Args:
        msg (str): The output message to parse.

    Returns:
        string: A string representing the results:
            - "done" -- means that the command was successful
            - "unknown" -- means an error has occurred and should be handled
                by the caller.

    """
    if msg.find('opened for add') != -1:
        return 'done'

    return 'unknown'


def _parse_delete_message(msg: str):
    """
    Parse the message received from P4 after a delete command.

    Args:
        msg (string): The output message to parse.

    Returns:
        string: A string representing the results:
            - "done" -- means that the command was successful
            - "unknown" -- means an error has occurred and should be handled
                by the caller.

    """
    if msg.find('opened for delete') != -1:
        return 'done'

    if msg.find('file(s) not on client') != -1:
        return 'done'

    return 'unknown'


def _revert_unchanged_files_in_p4():
    """
    Trigger a revert of all unchanged files on our changelists.

    Returns:
        None.

    """
    command = project_utility.get_p4_tool_path() + ' revert -a'
    successfull_command_call, \
        command_results = external_process_utility.trigger_external_subprocess(
            command)
    if not successfull_command_call:
        error_msg = (f'Encountered an error when'
                     f' reverting unchanged files: {command_results}')
        logging.error(error_msg)


def _revert_config_file_changes():
    """
    Revert the Config file changes to the previous step.

    Returns:
        None.

    """
    command = 'git checkout -- bin/GitterDone/Config.py'
    successfull_command_call, \
        command_results = external_process_utility.trigger_external_subprocess(
            command)
    if not successfull_command_call:
        error_msg = (f'Encountered an error reverting Config.py changes.'
                     f' Response: {command_results}')
        logging.error(error_msg)


def _checkout_files_in_p4(file_list: list):
    """
    Walk through a list of files and checks them out in p4.

    Args:
        file_list (list): The list of files to be checked out.

    Returns:
        list: A list of files that exist locally but not on P4
              and must passed to the Add command.

    """
    pretty_checkout_list = string_utility.friendly_list_to_str(file_list)
    logging.info('Checking out the following files: %s', pretty_checkout_list)
    files_to_add = []
    for file in file_list:
        if file not in IGNORED_P4_FILE_LIST:
            successful_checkout, file_to_add = _checkout_file_in_p4(file)
            if successful_checkout:
                if file_to_add and (file_to_add not in files_to_add):
                    files_to_add.append(file_to_add)

    if files_to_add:
        return files_to_add

    return None


def _checkout_file_in_p4(file_path: str):
    """
    Trigger an P4 Checkout for an individual file.

    Args:
        file_path (str): The path of the file to be checked out.

    Returns:
        bool: Flag determining whether if the file was checked out or slotted
            for addition successfully.
        str: The path for a file that couldn't be checked out as it didn't
            exist on P4 and must be added.

    """
    if not file_path:
        logging.error(
            ('Attempted to trigger an empty p4 edit command.'
             ' Please troubleshoot file list.'))
        return False, None

    command = (project_utility.get_p4_tool_path() +
               ' edit \"' +
               file_path +
               '\"')

    successfull_command_call, \
        command_results = external_process_utility.trigger_external_subprocess(
            command)

    if not successfull_command_call:
        logging.error('An error occurred: %s', command_results.output)
        return False, None

    first_line = (command_results.splitlines())[0]

    result = _parse_edit_message(first_line)

    if result == 'add':
        return True, file_path

    if result == 'unknown':
        logging.error(('An unknown error occurred when'
                       ' attempting to check out %s', file_path))
        return False, None

    return True, None


def _add_files_to_p4(file_list: list):
    """
    Walk through a list of files and adds them out in P4.

    Args:
        file_list (list): The list of files to be added to P4.

    """
    pretty_add_list = string_utility.friendly_list_to_str(file_list)
    logging.info(('Found files that were not on P4.'
                  ' Adding the following files: %s', pretty_add_list))

    for file in file_list:
        _add_file_to_p4(file)


def _add_file_to_p4(file_path: str):
    """
    Trigger an P4 add command for an individual file.

    Args:
        file_path (str): The path of the file to be added.

    Returns:
        None.

    """
    if not file_path:
        logging.error(('Attempted to trigger an empty p4'
                       ' add command. Please troubleshoot file list.'))

    else:
        command = (project_utility.get_p4_tool_path() +
                   ' add \"' +
                   file_path +
                   '\"')

        successfull_command_call, \
            command_results = (external_process_utility.
                               trigger_external_subprocess(
                                command))

        if not successfull_command_call:
            logging.error('An error occurred: %s', command_results.output)
            return

        first_line = (command_results.splitlines())[0]

        result = _parse_add_message(first_line)

        if result == 'unknown':
            logging.error(('An unknown error occurred when'
                           ' attempting to add  %s', file_path))


def _delete_files_from_p4(file_list: str):
    """
    Walk through a list of files and check'em out and deletes them from P4.

    Args:
        file_list (str): The list of files to be deleted from P4.

    """
    pretty_file_list = string_utility.friendly_list_to_str(file_list)
    logging.info('Deleting the following files from P4: %s', pretty_file_list)

    for file in file_list:
        _delete_file_from_p4(file)


def _delete_file_from_p4(file_path: str):
    """
    Trigger an P4 delete command for an individual file.

    Args:
        file_path (str): The path of the file to be deleted.

    Returns:
        None.

    """
    if not file_path:
        logging.error(('Attempted to trigger an empty p4 delete'
                       ' command. Please troubleshoot file list.'))

    else:
        command = (project_utility.get_p4_tool_path() +
                   ' delete \"' +
                   file_path +
                   '\"')

        successfull_command_call, \
            command_results = (external_process_utility.
                               trigger_external_subprocess(
                                   command))

        if not successfull_command_call:
            logging.error('An error occurred: %s', command_results.output)
            return

        first_line = (command_results.splitlines())[0]

        result = _parse_delete_message(first_line)

        if result == 'unknown':
            logging.error(('An unknown error occurred when attempting'
                           ' to delete %s', file_path))


def execute_p4_offline_sync(
        desired_branch: str,
        include_trunk_branch: bool,
        ignored_branches: list = None):
    """
    Execute the P4 offline sync.

    This functions walks through a branch's list of modified files,
    Checks them out on P4 and then reverts all unchanged.

    Args:
        desired_branch (str): String representing the branch to query which
            files were modified.
        include_trunk_branch (bool): Flag determining if we should include
            changes from the trunk branch as well.
        ignored_branches (list, optional): List of branches that should be
            ignored when extracting changes from the git branch.

    """
    _execute_p4_offline_sync(desired_branch,
                             include_trunk_branch,
                             ignored_branches)


def _execute_p4_offline_sync(  # pylint:disable=R0912
        desired_branch: str,
        include_trunk_branch: bool,
        ignored_branches: list = None):
    """
    Extract all the changes in a branch into  a P4 changelist.

    Args:
        desired_branch (str): the name of the branch we want to extract the
            changes from.
        include_trunk_branch (bool): A flag representing whether we should
            include the changes in the trunk branch in the CL.
        ignored_branches (list, optional): A list of branches to ignore when
            getting the modified files.

    Returns:
        None.

    """
    logging.info('Executing P4 offline sync')

    if not desired_branch:
        logging.error(('No branch specified, prompt user if they want'
                       'to check out everything.'))

        get_all_modified = True

        if include_trunk_branch:
            get_all_modified = console_utility.request_user_input_with_choices(
                ('No Branch specified, Check out ALL modified files'
                 ' in the git repo? [CAUTION: HUGE CHANGELIST POTENTIAL]'),
                'y/n',
                'y',
                'n')
        else:
            message = ('No Branch specified, Check out modified files in'
                       ' the git repo with the exception of files from the'
                       ' \"%s\" Branch', TRUNK_BRANCH_NAME)
            get_all_modified = console_utility.request_user_input_with_choices(
                message, 'y/n', 'y', 'n')

        # Terminate
        if not get_all_modified:
            logging.info(('User does not desire to get all files in the'
                          ' branch. Stopping execution.'))
            return

    #  Get all the branches.
    available_git_branches = git_utility.get_git_branch_information()

    # Check if the branches being requested to ignore exist.
    ignored_branches_str = ''

    if ignored_branches is not None:
        for ignored_branch in ignored_branches:
            if git_utility.verify_branch_exists_in_git(
                    ignored_branch,
                    available_git_branches):
                ignored_branches_str += f'{ignored_branch.lower()} '

    if not git_utility.verify_branch_exists_in_git(
            desired_branch,
            available_git_branches):
        branches = string_utility.friendly_list_to_str(available_git_branches)
        logging.fatal(('Input branch \'%s\' does not match any of'
                       ' the desired names: %s',
                       desired_branch,
                       branches))
        return

    if not git_utility.verify_branch_exists_in_git(
            TRUNK_BRANCH_NAME,
            available_git_branches):
        branches = string_utility.friendly_list_to_str(available_git_branches)
        logging.fatal(('Sync branch in Config.py: \'%s\' does not exist'
                       ' in the repository: %s', TRUNK_BRANCH_NAME, branches))
        return

    files_to_add_or_edit, files_to_delete = (
        git_utility.get_modified_files_for_branch(
            desired_branch,
            include_trunk_branch,
            TRUNK_BRANCH_NAME,
            ignored_branches_str)
        )

    if files_to_delete:
        _delete_files_from_p4(files_to_delete)

    if files_to_add_or_edit:
        files_to_add = _checkout_files_in_p4(files_to_add_or_edit)
        if files_to_add:
            _add_files_to_p4(files_to_add)

    if not files_to_delete and not files_to_add_or_edit:
        logging.error('The file list is empty.')

    _revert_unchanged_files_in_p4()


def _execute_forced_sync_in_p4_to_cl(change_list_number: str,
                                     files_to_sync: list):
    """
    Perform a forced sync of any folder in the FORCED_SYNC_WISHLIST.

    Args:
        change_list_number (str): A string containing the CL to sync to.
        files_to_sync (list): the list of files & folders we are to
            forcefully sync.

    Returns:
        bool: True if the sync command was successful.

    """
    project_root_path = project_utility.get_project_root_path()
    p4_tool_path = project_utility.get_p4_tool_path()

    logging.debug('Forcefully syncing: %s',
                  string_utility.friendly_list_to_str(files_to_sync))

    for entry in files_to_sync:

        path = string_utility.normalize_string(os.path.join(
                        project_root_path,
                        entry),
                                            remove_wildcards=True)

        if os.path.exists(path):
            if os.path.isdir(path):
                if path.endswith('/'):
                    absolute_path = path + '...'
                else:
                    absolute_path = path + '/...'
            elif os.path.isfile(path):
                absolute_path = path

            # check if the absolute path exist!
            logging.info('Executing a forced sync of %s', absolute_path)

            command = p4_tool_path + ' sync -f '\
                + string_utility.normalize_string(
                    absolute_path + '@' + change_list_number)

            successfull_command_call, \
                command_results = (external_process_utility.
                                   trigger_external_subprocess(
                                       command))

            if successfull_command_call:
                logging.info('%s Forced sync completed.', absolute_path)
            else:
                logging.error('%s Forced sync unsuccessful. Response:\n %s',
                              absolute_path,
                              command_results)
                return False
        else:
            error_msg = (f'File \"{absolute_path}\" no longer exists.'
                         f' Ignoring sync')
            logging.error(error_msg)
            return True
    return True


def _execute_p4_smart_sync_to_cl(change_list_number: str, file_path: str):
    """
    Perform a smart sync of the entire project.

    Args:
        change_list_number (str): A string containing the CL to sync to.
        file_path (str): The file path to trigger the smart sync on.

    Returns:
        bool: True if the sync command was successful.

    """
    logging.info('Executing a sync of %s To CL:%s',
                 file_path,
                 change_list_number)

    if os.path.isdir(file_path):
        if file_path.endswith('/'):
            absolute_path = file_path + '...'
        else:
            absolute_path = file_path + '/...'

    if not os.path.exists(absolute_path):
        error_msg = f'File \"{absolute_path}\" no longer exists. Ignoring sync'
        logging.error(error_msg)
        return True

    command = project_utility.get_p4vfs_tool_path() + " sync -f " + \
        string_utility.normalize_string(absolute_path +
                                        "@" +
                                        change_list_number)

    successfull_command_call, \
        command_results = (external_process_utility.
                           trigger_external_subprocess(
                               command))

    if successfull_command_call:
        logging.info('%s Sync completed successfully.', absolute_path)

    else:
        logging.info('%s Sync unsuccessful, terminating. Response: %s',
                     absolute_path,
                     command_results)
        return False
    return True


def _sync_p4_to_changelist(desired_cl: str, force_all: bool = False):
    """
    Trigger all the sync steps to sync P4 to a changelist.

    Args:
        desired_cl (str): A string containing the CL to sync to.
        force_all (bool, optional): A flag representing whether we should sync
            every entry of the wishlist individually.

    Returns:
        bool: True if the sync command was successful.

    """
    logging.info('Updating %s to CL %s',
                 project_utility.get_project_root_path(),
                 desired_cl)

    if force_all:
        logging.info('Forcefully updating everything tracked.')
        if not _execute_forced_sync_in_p4_to_cl(
                desired_cl, GIT_FILE_WISHLIST + FORCED_SYNC_WISHLIST):
            return False
    else:
        logging.info('Forcefully updating items on the FORCED_SYNC_WISHLIST')
        if not _execute_forced_sync_in_p4_to_cl(
                desired_cl,
                FORCED_SYNC_WISHLIST):
            return False

    # We should have successfully synced by this point.
    if not _execute_p4_smart_sync_to_cl(
            desired_cl,
            project_utility.get_project_root_path()):
        return False

    return True


def execute_git_sync_with_p4(desired_changelist: str,
                             forced: bool = False,
                             force_all: bool = False,
                             bypass_prompts: bool = False):
    """
    Attempt to perform a full sync with the current version of the source.

    Args:
        desired_changelist (str): A string representing the CL that we should
            sync everything to.
        forced (bool, optional): A flag representing whether we should still
            sync regardless.
        force_all (bool, optional): A flag representing whether we should sync
            every entry of the wishlist individually.

    No Longer Returned:
        None.

    """
    _execute_git_sync_with_p4(desired_changelist,
                              forced,
                              force_all,
                              bypass_prompts)


def _execute_git_sync_with_p4(desired_changelist: str,
                              forced: bool = False,
                              force_all: bool = False,
                              bypass_prompts: bool = False):
    logging.info('Syncing Git & P4.')
    should_stage_changes = len(desired_changelist) > 0
    should_interrupt = False

    if should_stage_changes:
        logging.info('Updating repository up to CL %s', desired_changelist)
    else:
        logging.info(
            'Updating repository with the latest CL in git trunk branch.')

    if (not git_utility.check_and_resolve_pending_git_changes(bypass_prompts)
            or not git_utility.check_and_resolve_if_user_is_on_branch(
                TRUNK_BRANCH_NAME,
                bypass_prompts)):
        return

    result, detected_changelist = git_utility.verify_branch_up_to_date(
        TRUNK_BRANCH_NAME,
        desired_changelist,
        forced,
        bypass_prompts)

    if not result and not detected_changelist:
        logging.fatal(('Unsuccessful verification of git branch'
                       ' parity with no resolution message.'))
        should_interrupt = True

    if not result and int(detected_changelist) and not should_interrupt:
        logging.debug('Git raised that we should sync P4 to CL %s',
                      detected_changelist)
        if not _sync_p4_to_changelist(detected_changelist, force_all):
            logging.fatal('Sync to %s failed.', detected_changelist)
            should_interrupt = True

    logging.info('Enviroment is now up to date with git repository.')

    if should_interrupt:
        return

    if should_stage_changes:
        if not _sync_p4_to_changelist(desired_changelist, force_all):
            logging.fatal('Sync to %s failed.', desired_changelist)
            return

        _revert_config_file_changes()

        if not git_utility.stage_git_changes():
            return

        commit_message = 'CL ' + desired_changelist
        if not git_utility.commit_git_changes(commit_message):
            return
