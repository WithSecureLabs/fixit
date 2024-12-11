"""
options_get.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Get` command, which allows users to retrieve the value
    of a specific option in the Fixit application. It provides a simple interface
    for accessing configuration or runtime properties.

Key Features:
    - Accesses the value of a specific option by its name.
    - Supports output to the console for user feedback.
    - Returns the value programmatically for further processing.

Usage:
    The `Get` command is used to retrieve the value of an option. Example:
        ```python
        get_cmd = Get("options_get")
        option_value = get_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            name="resp_delay"
        )
        print(option_value)  # Outputs the value of the "verbose" option
        ```
    Arguments:
        - `name`: The name of the option to retrieve (required).
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
        self.set_description("Gets the value of a specific option")
        self._init_arg_parser([
            {
                "name": "name",
                "data": {
                    "metavar": "<NAME>",
                    "help": "The options value to view",
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
            return None

        if run_ctx.output:
            run_ctx.cli.writer.print(f"{args.name} = {value[OPT_VAL]}")

        return value
