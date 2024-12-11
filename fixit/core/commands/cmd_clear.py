"""
cmd_clear.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Clear` command, which is used to clear the terminal screen
    and reset the application interface.

Usage:
    ```python
    clear_cmd = Clear()
    clear_cmd.run(cli=cli_instance, user_input="")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Clear"]

class Clear(Command):
    """
    A command to clear the CLI interface of acticity.

    The `Clear` command is used to clear the terminal screen
    and reset the application interface.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Clear's the application interface")
        self._init_arg_parser()


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx)

        run_ctx.cli.writer.clear()
