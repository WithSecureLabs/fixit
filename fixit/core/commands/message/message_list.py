"""
message_list.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `List` command, which provides functionality to list all
    messages stored in the current message store. It supports filtering messages
    based on user-specified criteria using regular expressions.

Key Features:
    - Lists all messages in the message store with an optional filter.
    - Supports regex-based filtering for flexible message matching.
    - Displays messages in a tabular format for better readability.
    - Dynamically updates autocomplete suggestions based on available commands and message IDs.

Usage:
    The `List` command is executed to view messages in the message store. Example:
        ```python
        list_cmd = List("message_list")
        list_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            filter=".*ORDER.*"
        )
        ```
    Arguments:
        - `filter`: An optional regex pattern to filter messages by their IDs.
"""

import re
import readline

from colorama import Fore

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class List(Command):
    """ List messages within the message store """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("List messages within the message store")
        self._init_arg_parser([
            {
                "name": "filter",
                "data": {
                    "metavar": "[FILTER]",
                    "help": "A string used to filter the message store",
                    "type": str.upper,
                    "nargs": "?"
                }
            },
        ])
        self.set_example([
            "message list                 - List all messages in the message store"
            "message list \".*ORDER.*\"   - List all messages with ORDER in the name",
            "message list \".*ORDER.*\" 2 - List last 2 messages with ORDER in the name",
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, _ = self.parse_input(run_ctx)
        if args.filter is None:
            args.filter = ".*"

        try:
            regex = re.compile(args.filter)
            self.display_messages(run_ctx, regex)

        except(re.error) as error:
            run_ctx.cli.writer.error(
                f"Invalid filter '{args.filter}': {error}"
            )


    def display_messages(self, run_ctx, re_filter):
        """ Display messages based on the filter """
        matches = [
            msg for msg_id, msg in run_ctx.cli.message_store.store.items()
            if (bool(re.match(re_filter, msg['id'])) or bool(re.match(re_filter, msg['msg'])))
        ]

        margin, table = 0, []
        for msg in matches:
            margin = len(msg['id']) if len(msg['id']) > margin else margin

        for msg in matches:
            table.append([
                run_ctx.cli.writer.colour(msg['id'].ljust(margin), Fore.LIGHTCYAN_EX),
                run_ctx.cli.writer.limit(msg['msg'], margin+2)
            ])

        run_ctx.cli.writer.table(table, ["ID", "Message"])

        words = [cmd.lower() for cmd in run_ctx.cli.commands]
        words.extend([msg['id'] for msg in matches])
        readline.set_completer(SimpleCompleter(words).complete)
        readline.parse_and_bind('tab: complete')
