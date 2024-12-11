"""
cmd_options.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Options` command, which provides access to and management
    of Fixit application options.

    The `Options` class extends the `Command` base class and allows users to:
    - LIST: Displays all available options along with their current values.
    - GET: Retrieves the value of a specific option.
    - SET: Modifies the value of a specific option.

Usage:
    ```python
    options_cmd = Options()
    options_cmd.run(cli=cli_instance, user_input="get verbose")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

from fixit.core.commands.options import *

__all__ = ["Options"]

class Options(Command):
    """
    A command to manage and interact with Fixit CLI options.

    The `Options` command provides tools for accessing, modifying, and displaying
    fixit cli options properties.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Displays the application's options")
        self._init_arg_parser([
            {
                "name": "action",
                "data": {
                    "help": ARGS_ACTION_DESC,
                    "choices": ["LIST", "GET", "SET"],
                    "type": str.upper,
                    "nargs": "?",
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
        actions = self.parser_args["action"].choices
        args, args_trail = self.parse_input(run_ctx, actions)

        if args.action is None:
            self._options_list(run_ctx, args, user_input=args_trail)
            return

        # Run action options_<action>() function
        self.run_action(run_ctx, args, user_input=args_trail, prefix="_options_")


    def _options_list(self, run_ctx, args, user_input):
        """ Lists the current options in a table format """
        table = []
        for name, data in run_ctx.cli.options.items():
            table.append([name, data[OPT_VAL], data[OPT_DESC]])

        run_ctx.cli.writer.table(table, ["Option", "Value", "Description"], "User Options")


    def _options_get(self, run_ctx, args, user_input):
        """ Executes the options_get sub-command """
        Get(f"{self.name} get").run(
            user_input = user_input,
            source_dict = run_ctx.cli.options,
            output = True,
            cli = run_ctx.cli
        )


    def _options_set(self, run_ctx, args, user_input):
        """ Executes the options_set sub-command """
        Set(f"{self.name} set").run(
            user_input = user_input,
            cli = run_ctx.cli
        )
        self._options_get(run_ctx, args, user_input)
