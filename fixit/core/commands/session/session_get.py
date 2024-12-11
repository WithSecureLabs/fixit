"""
session_get.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Get` command, which allows users to retrieve the value
    of a specific session property in the Fixit application. It provides a simple interface
    for accessing configuration or runtime session properties.

Key Features:
    - Accesses the value of a specific session property by its name.
    - Supports output to the console for user feedback.
    - Returns the value programmatically for further processing.

Dependencies:
    - fixit.core.commands.cmd
    - fixit.core.constants
    - fixit.utils.common

Usage:
    The `Get` command is used to retrieve the value of a session property. Example:
        ```python
        get_cmd = Get("options_get")
        session_value = get_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            name="HeartBtInt"
        )
        print(session_value)  # Outputs the value of the "HeartBtInt" session property
        ```
    Arguments:
        - `name`: The name of the session property to retrieve (required).
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Get(Command):
    """ Gets the value of a key """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Gets the value of a specific session setting")
        self._init_arg_parser([
            {
                "name": "name",
                "data": {
                    "metavar": "<NAME>",
                    "help": "The session config value to view",
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
        value = Utils.dict_get_value(run_ctx.source_dict, args.name)

        if value == INVALID:
            return

        run_ctx.cli.writer.print(f"{args.name} = {value}")
