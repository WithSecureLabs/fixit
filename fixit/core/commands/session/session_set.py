"""
session_set.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Set` command, which allows users to modify the value of
    specific session property in the Fixit application. It provides a simple interface for
    updating configuration or runtime session properties dynamically.

Key Features:
    - Updates the value of a specified session property.
    - Supports dynamic updates to sensitive credentials such as username and password.
    - Ensures validity of certain options, such as session identifiers, before applying changes.
    - Integrates with the client to update runtime behaviors like logging and session management.

Dependencies:
    - fixit.core.commands.cmd
    - fixit.core.constants
    - fixit.utils.common

Usage:
    The `Set` command is used to modify the value of a session property. Example:
        ```python
        set_cmd = Set("options_set")
        set_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            name="HeartBtInt", value="30"
        )
        ```
    Arguments:
        - `name`: The name of the session property to modify (required).
        - `value`: The new value to assign to the session property (required).
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
        self.set_description("Sets the value of a specific session setting")
        self._init_arg_parser([
            {
                "name": "name",
                "data": {
                    "metavar": "<NAME>",
                    "help": "The session config value to set",
                }
            },
            {
                "name": "value",
                "data": {
                    "metavar": "<VALUE>",
                    "help": "The new session config value",
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

        run_ctx.cli.client.set_session_config(
            args.name, args.value,
            run_ctx.session_num
        )
