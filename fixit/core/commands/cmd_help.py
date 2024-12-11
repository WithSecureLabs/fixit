"""
cmd_help.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Help` command, which provides an overview
    of the available application commands.

Usage:
    ```python
    help_cmd = Help()
    help_cmd.run(cli=cli_instance, user_input="")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Help"]

class Help(Command):
    """
    A command to clear the CLI interface of acticity.

    The `Help` command is used to return the high-level help information to
    the end user. This is used to utline all core commands provided by Fixit
    """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Displays the application help")
        self._init_arg_parser()


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx)

        table = []
        for cmd_name, cmd_inst in run_ctx.cli.commands.items():
            table.append([cmd_name.lower(), cmd_inst.get_description()])

        run_ctx.cli.writer.table(table, ["Command", "Description"], "Core Commands")
