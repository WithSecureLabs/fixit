"""
cmd_banner.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Banner` command, which is used to display the
    application's banner art along with its version information.

Usage:
    ```python
    banner_cmd = Banner()
    banner_cmd.run(cli=cli_instance, user_input="")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Banner"]

class Banner(Command):
    """
    A command to display the application's banner art and version information.

    The `Banner` command is used to print a visually styled banner for the Fixit
    application, including its version number. It is typically displayed at the
    start of the application or on user request.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Displays the application banner")
        self._init_arg_parser()


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx)

        run_ctx.cli.writer.print(BANNER, RED)
        run_ctx.cli.writer.print(" "*19 + f"version {VERSION}")
