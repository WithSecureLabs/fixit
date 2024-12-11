"""
cmd.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the main `Command` class, which serves as the base class for
    all application command objects in the Fixit framework. The `Command` class provides
    a consistent interface for argument parsing, input validation, and command execution.

    The design of this class ensures extensibility and uniformity across all command
    implementations, allowing for easy integration into the application's command-line
    environment.

Key Features:
    - Argument Parsing: Handles argument parsing with support for static and variable
      commands.
    - Input Validation: Provides automatic session and message context setting, along
      with session validation.
    - Action Execution: Dynamically executes subcommands based on user input.

Usage:
    The `Command` class is intended to be inherited by specific command
    implementations, which define their own arguments and execute customized
    behavior within the `run()` method.
"""

import traceback

#pylint: disable=unused-import # Used when inherited
from types import SimpleNamespace

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.utils.parser import *
from fixit.core.constants import *

class Command():
    """
    A base class for defining application commands in the Fixit framework.

    The `Command` class provides a unified interface for parsing arguments, validating inputs,
    and executing commands. It ensures consistency across command implementations and simplifies
    integration into the application's command-line environment.

    Attributes:
        name (str): Name of the command
        description (str): Description of the command
        parser (ArgumentParser): Parser for the command
        parser_args (dict): Arguments for the parsers
        cmd_type (str): THe type of commans (Static / varialbe)
    """

    def __init__(self, name):
        """ Initializes the command with a name and sets up argument parsing. """
        self.name = name
        self.description = ""
        self.parser = ArgumentParser(prog=self.name, add_help=False)
        self.parser_args = {}
        self.cmd_type = ""


    def parse_input(self, run_ctx, actions=None, auto_session=False, auto_message=False):
        """
        Parses user input and returns parsed arguments and trailing arguments.

        Args:
            run_ctx (SimpleNamespace): The runtime context containing user input and CLI state.
            actions (list, optional): A list of valid subcommands for the command. Defaults to None.
            auto_session (bool, optional): Whether to automatically set the session. Defaults to False.
            auto_message (bool, optional): Whether to automatically set the message ID. Defaults to False.

        Returns:
            tuple: Parsed arguments (args) and remaining arguments (args_trail).

        Raises:
            NeedHelpException: If the user requests help for the command.
            InvalidArgsError: If the argument parsing fails.
            InvalidSessionError: If the session specified is invalid.
        """
        args, args_trail = None, None
        actions = [] if actions is None else actions

        if auto_session:
            self._auto_set_session(run_ctx)

        if auto_message:
            if len(run_ctx.cli.get_message_ctx()) != 0:
                self._auto_set_message(run_ctx)

        # Check if command is STATIC or VARIABLE
        if len(run_ctx.user_input) == 0 and self.cmd_type == CMD_STATIC:
            return None, None

        # Check if a nested command exists
        has_nested_cmd = False
        for key_word in run_ctx.user_input:
            if str(key_word).upper() in actions:
                has_nested_cmd = True
                break

        if self._check_help(run_ctx.user_input, has_nested_cmd):
            raise NeedHelpException()

        args, args_trail = self.parser.parse_known_args_silent(args=run_ctx.user_input)
        if args is None:
            raise InvalidArgsError()

        # Check if the session used exists on the client
        if hasattr(args, "session_num"):
            if not run_ctx.cli.client.has_session(args.session_num, output=True):
                raise InvalidSessionError()

        return args, args_trail


    def set_description(self, description):
        """ Sets the description string for the command """
        self.parser.description = description


    def get_description(self):
        """ Returns the description string for the command """
        return self.parser.description


    def set_example(self, example_lines):
        """ Sets the Example string for the command """
        self.parser.formatter_class=argparse.RawDescriptionHelpFormatter
        self.parser.epilog = "Example:\n  " + '\n  '.join(example_lines)


    def run_action(self, run_ctx, args, user_input, prefix=""):
        """
        Executes a subcommand based on a prefix and user-provided action.
        # Constructs and executes the function <prefix>_<action>(user_args)

        Args:
            run_ctx (SimpleNamespace): The runtime context containing CLI state.
            args (argparse.Namespace): Parsed arguments for the command.
            user_input (list): User input to pass to the action function call
            prefix (str, optional): Prefix that defines the action method name.
        """
        try:
            getattr(self, f"{prefix}{args.action.lower()}")(
                run_ctx, args, user_input
            )
        except (AttributeError) as error:
            print(f"{ERR_MSG_CM01}: {error}")
            #traceback.print_exc()
            #print(stack_trace)


    def _init_arg_parser(self, cmd_args=None):
        """
        Initializes the command's argument parser with provided arguments.

        Args:
            cmd_args (list, optional): A list of dictionaries representing command arguments. Defaults to None.
        """
        cmd_args = [] if cmd_args is None else cmd_args
        self.cmd_type = self._classify_cmd_type(cmd_args)

        # If the command is static, dont parse any arguments
        if self.cmd_type == CMD_STATIC:
            return

        for arg in cmd_args:
            self.parser_args[arg["name"]] = self.parser.add_argument(
                arg["name"], **arg["data"]
            )


    def _classify_cmd_type(self, cmd_args):
        """ Classifies a command based on its argument count into STATIC (0) or VARIABLE (1+) """
        if len(cmd_args) > 0:
            return CMD_VARIABLE

        return CMD_STATIC


    def _auto_set_message(self, run_ctx):
        """ Automatically prepends a message ID in the user's input data if not provided. """
        if (len(run_ctx.user_input) == 0 or # If no message ID set
            run_ctx.user_input[0] not in run_ctx.cli.message_store.store
        ):
            run_ctx.user_input.insert(0, run_ctx.cli.get_message_ctx()['id'])


    def _auto_set_session(self, run_ctx):
        """ Automatically sets a session type for the command if not provided """
        if (
            len(run_ctx.user_input) == 0 or # If no session ID set
            run_ctx.user_input[0] not in run_ctx.cli.client.sessions.keys()
        ):
            run_ctx.user_input.insert(0, run_ctx.cli.options["session"][OPT_VAL])


    def _check_help(self, user_input, has_nested_cmd):
        """
        Checks if the user requested help or usage information for the command.

        Args:
            user_input (list): The user's input arguments.
            has_nested_cmd (bool): Whether the command has a nested subcommand.

        Returns:
            bool: True if help or usage was requested, False otherwise.
        """
        if has_nested_cmd is False:
            for _val in user_input:
                if str(_val).upper() == "HELP":
                    self.parser.print_help()
                    return True

                if str(_val).upper() == "USE":
                    self.parser.print_usage()
                    return True

        return False
