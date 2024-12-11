"""
parser.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines a custom argument parser used by application commands in the Fixit application.
    The primary goal of the custom parser is to handle unknown or unexpected arguments silently,
    allowing the application to continue functioning without abrupt exits or unnecessary help messages.

Key Features:
    - Silent Argument Parsing: Allows parsing of arguments without outputting errors or
      exiting the application.
    - Autocompletion Support: Implements basic autocompletion for CLI commands.
    - Enhanced Error Handling: Raises custom exceptions (`InvalidArgsError`) instead of
      default argparse errors, enabling better integration with the application.

Usage:
    Example usage of the custom parser:
        ```python
        parser = ArgumentParser(prog="example")
        parser.add_argument("command", help="Specify a command to execute.")
        args = parser.parse_args_silent(["unknown_command"])
        ```
    Example usage of the autocompleter:
        ```python
        completer = SimpleCompleter(["start", "stop", "restart"])
        matches = completer.complete("st", 0)  # Returns "start"
        ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
import argparse
from fixit.utils.exceptions import *

#pylint: disable=too-few-public-methods
class SimpleCompleter():
    """
    Implements basic autocompletion for the Fixit CLI commands.

    The `SimpleCompleter` class provides a mechanism to suggest matches
    for partially typed input based on a predefined list of options.

    Attributes:
        options (list): A sorted list of available options for autocompletion.
        matches (list): A list of potential matches for the current input.
    """
    def __init__(self, options):
        self.options = sorted(options)
        self.matches = []


    def complete(self, text, state):
        """
        Provides autocompletion suggestions for the given text.

        Args:
            text (str): The current input text to complete.
            state (int): The state index for cycling through matches.

        Returns:
            str or None: The next matching option, or None if no matches are available.
        """
        if state == 0:
            if text:
                self.matches = [
                    string for string in self.options
                    if string and string.startswith(text)
                ]
            else:
                self.matches = self.options[:]

        try:
            return self.matches[state]

        except IndexError:
            return None


class ArgumentParser(argparse.ArgumentParser):
    """
    Custom argument parser for interactive Fixit CLI commands.

    The `ArgumentParser` class extends the built-in `argparse.ArgumentParser`
    to provide silent error handling and enhanced functionality for Fixit commands.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._positionals.title = "Arguments"


    def error(self, message):
        """ Override default error function to avoide auto printing help and exiting """
        raise InvalidArgsError()


    def parse_known_args_silent(self, args=None):
        """ Parses and returns known and unknown arguments without raising an error on failure """
        result, unknown = super().parse_known_args(args)
        return result, unknown


    def parse_args_silent(self, args=None):
        """ Parses and returns known arguments without raising an error on failure """
        result, _ = super().parse_known_args(args)
        return result
