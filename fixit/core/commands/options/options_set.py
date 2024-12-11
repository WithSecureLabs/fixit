"""
options_set.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Set` command, which allows users to modify the value of
    specific options in the Fixit application. It provides a simple interface for
    updating configuration or runtime properties dynamically.

Key Features:
    - Updates the value of a specified option.
    - Supports dynamic updates to sensitive credentials such as username and password.
    - Ensures validity of certain options, such as session identifiers, before applying changes.
    - Integrates with the client to update runtime behaviors like logging and session management.

Usage:
    The `Set` command is used to modify the value of an option. Example:
        ```python
        set_cmd = Set("options_set")
        set_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            name="resp_delay", value="0.5"
        )
        ```
    Arguments:
        - `name`: The name of the option to modify (required).
        - `value`: The new value to assign to the option (required).
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Set(Command):
    """ Sets the value of a key """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Sets the value of a specific option")
        self._init_arg_parser([
            {
                "name": "name",
                "data": {
                    "metavar": "<NAME>",
                    "help": "The options value to set",
                }
            },
            {
                "name": "value",
                "data": {
                    "metavar": "<VALUE>",
                    "help": "The new option value",
                }
            },
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx) #pylint: disable=unused-variable

        if args.name in run_ctx.cli.options:

            if args.name.upper() == "PASSWORD":
                run_ctx.cli.client.set_password(args.value)
            if args.name.upper() == "USERNAME":
                run_ctx.cli.client.set_username(args.value)
            if args.name.upper() == "LOG_HEARTBEAT":
                run_ctx.cli.client.set_log_heartbeat(bool(args.value))

            if args.name.upper() == "SESSION":
                if args.value not in run_ctx.cli.client.sessions.keys():
                    return

            run_ctx.cli.set_option(args.name, args.value)

        return
