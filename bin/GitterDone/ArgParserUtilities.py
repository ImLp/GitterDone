"""
Parser Module.

This module set ups the argument parsing functionality.
"""
import argparse


def add_parser_option(parser: argparse,
                      short_name: str = '',
                      full_name: str = '',
                      **kwargs):
    """
    Add a new option to the Parser.

    This function allows us to add a new option to the argument parser. This
    allows for every module with an entry point to set up its own set of
    arguments for multi-module startup.

    Args:
        parser (argparse): The parser we are adding the new option to.
        short_name (str): The short name of the command line flag. e.g. '-f'.
        full_name (str): The fully descriptive command line flag e.g. '--foo'.
        **kwargs: The optional parameters that will be added to the parser.
          see cref: https://github.com/python/cpython/blob/3.7/Lib/argparse.py.

    """
    if short_name and full_name:
        parser.add_argument(
            short_name,
            full_name,
            **kwargs)
    else:
        parser.add_argument(full_name, **kwargs)


def setup_parser(bare: bool = False, help_message: str = ''):
    """
    Parser constructor.

    Adds all the parser commands that the command line allows along with their
        usage information.

    """
    if help_message:
        parser = argparse.ArgumentParser(usage=help_message)
    else:
        parser = argparse.ArgumentParser()

    if not bare:
        add_parser_option(
            parser,
            "-l",
            "--loglevel",
            help="Increase or decrease program verbosity.",
            type=str,
            choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'],
            default="INFO")

    return parser
