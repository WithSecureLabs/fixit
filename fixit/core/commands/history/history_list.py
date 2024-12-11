"""
history_list.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `List` command, which provides functionality for displaying
    the FIX message history of the active session in a tabular format. It is a component
    of the history command suite within the Fixit application.

Key Features:
    - Retrieves message history for the active session.
    - Supports configurable depth to control the number of messages displayed.
    - Allows filtering messages using a string pattern.
    - Displays messages in a table format.

Usage:
    The `List` command is executed to display the FIX message history. Example:
        ```python
        list_cmd = List("history_list")
        list_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli
        )
        ```
    Arguments can be passed to control the depth and filter:
        - `depth`: Specifies the number of recent messages to display (default: 25).
        - `filter`: Filters the message history using a string pattern (default: ".*").
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class List(Command):
    """ Lists the applications message history """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Displays the session's message history")
        self._init_arg_parser([
            {
                "name": "depth",
                "data": {
                    "metavar": "[DEPTH]",
                    "help": "The amount of history to return",
                    "default": 50,
                    "type": int,
                    "nargs": "?"
                }
            },
            {
                "name": "filter",
                "data": {
                    "metavar": "[FILTER]",
                    "help": "A string used to filter the message history",
                    "default": ".*",
                    "type": str.upper,
                    "nargs": "?"
                }
            },
        ])
        self.set_example([
            "history list                  - List the message history",
            "history list 2                - List any of the last 2 items in message history",
            "history list \".*ORDER.*\"    - List any messages that are ORDERs",
            "history list 2 \".*ORDER.*\"  - List the last 2 ORDERS processed",
        ])

    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx)

        self._history_list(run_ctx, args, user_input=args_trail)


    def _history_list(self, run_ctx, args, user_input):
        """ Outputs the specified session's message history in table format """
        message_log = run_ctx.cli.client.get_session_message_log(
            run_ctx.session_num, args.filter, args.depth
        )

        table = []
        for row in message_log:
            str_id = str(row['id']).rjust(6)
            margin = len(str_id) + 2 + len(row["route"]) + 2

            if run_ctx.cli.writer.colour_mode:
                margin -= 9

            msg_str = run_ctx.cli.writer.limit(
                f"{row['type']} {row['msg']}", margin
            )

            table.append([str_id, row["route"], msg_str])

        run_ctx.cli.writer.table(table, ["ID", "Route", "Message"])
