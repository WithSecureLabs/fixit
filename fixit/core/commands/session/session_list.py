"""
session_list.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `List` command, which provides functionality to list all
    available FIX sessions defined withinin the initiator configuration. It displays the
    session details in a tabke format for user reference.

Key Features:
    - Retrieves all FIX sessions from the initiator configuration.
    - Displays session details, including session numbers and IDs.
    - Outputs the session list in a tabular format for better readability.

Dependencies:
    - fixit.core.commands.cmd
    - fixit.core.constants
    - fixit.utils.common

Usage:
    The `List` command is executed to display all available FIX sessions. Example:
        ```python
        list_cmd = List("session_list")
        list_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            source_dict=session_data
        )
        ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class List(Command):
    """ List available sessions """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Lists all available sessions")
        self._init_arg_parser()


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx) #pylint: disable=unused-variable

        table = []
        for session_num, session_obj in run_ctx.source_dict.items():
            table.append([session_num, session_obj["sessionID"]])

        run_ctx.cli.writer.table(
            table, ["Num", "sessionID"], "FIX Sessions"
        )
