"""
message_drop.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Drop` command, which provides functionality to drop
    the currently active message from the application's message context.
    It is used to drop the currnetly active message if it is no longer needed.

Key Features:
    - Clears the currently active message context.
    - Provides a straightforward mechanism to reset message usage.
    - Ensures no active message remains in the context after execution.

Usage:
    The `Drop` command is executed to clear the active message context. Example:
        ```python
        drop_cmd = Drop("message_drop")
        drop_cmd.run(cli=cli_instance)
        drop_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli
        )
        ```
    No additional arguments are required for this command.
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *

class Drop(Command):
    """ Drops the currently active FIX message """

    def __init__(self, name=""):
        """ Initializes the command with its name, description """
        super().__init__(name)
        self.set_description("Drops a message in use")
        self._init_arg_parser()


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx) #pylint: disable=unused-variable

        run_ctx.cli.clear_message_ctx()
