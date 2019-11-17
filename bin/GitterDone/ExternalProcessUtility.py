"""Handle calling external processes outside of git."""
import logging
import subprocess


def trigger_external_subprocess(command):
    """
    Trigger  an external subprocess command.

    Args:
        command (string): The command to be trigger by the subprocess.
        debug_mode (bool, optional): Flag to forego triggering the command if
            desired.

    Returns:
        bool: Value determining wether the command failed.
        string: The command's output if any.

    """
    logging.info("Triggering external command: %s", command)
    try:
        output = subprocess.check_output(command,
                                         stderr=subprocess.STDOUT,
                                         shell=True)

        result = output.decode(encoding="utf-8", errors="ignore")
        result = result.rstrip()
        logging.debug("Command Response:\n%s", result)
        return True, result
    except subprocess.CalledProcessError as ex:
        return False, ex


def trigger_external_subprocess_with_live_output(command):
    """
    Trigger  an external subprocess command.

    Args:
        command (string): The command to be trigger by the subprocess.
        debug_mode (bool, optional): Flag to forego triggering the command if
            desired.

    Returns:
        bool: Value determining wether the command failed.
        string: The command's output if any.

    """
    logging.info("Triggering external command: %s", command)
    try:
        process = subprocess.Popen(command,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        final_output = []
        while True:
            output = process.stdout.readline().decode(
                encoding="utf-8",
                errors="ignore")
            if output == '' and process.poll() is not None:
                break
            if output:
                output = output.rstrip()
                print(output.strip())
                final_output.append(output)

        results = "".join(final_output)
        logging.debug("Command Response:\n%s", results)
        return True, results
    except subprocess.CalledProcessError as ex:
        return False, ex
