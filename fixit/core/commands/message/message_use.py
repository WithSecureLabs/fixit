"""
message_use.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Use` command, enabling users to select and activate
    a specific FIX message from the message store for further operations such as
    viewing, editing, or sending.

Key Features:
    - Selects a message from the message store by its unique identifier.
    - Updates the application's message context with the selected message.
    - Prepares the selected message for subsequent actions like editing or sending.

Usage:
    The `Use` command is designed to streamline workflows by allowing the user to focus on a
    specific message for further operations. Example:
        ```python
        use_cmd = Use("message_use")
        use_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id="FIX.4.2:NEW_ORDER_D-D:1"
        )
        ```

    Arguments:
        - `msg_id`: Specifies the identifier of the message to be set as the active message.
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Use(Command):
    """ Sends a FIX message over a specified session """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Defines a specific message to use")
        self._init_arg_parser([
            {
                "name": "msg_id",
                "data": {
                    "metavar": "<MESSAGE ID>",
                    "help": "The message store ID to view",
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
        args, _ = self.parse_input(run_ctx)
        message_store = run_ctx.cli.message_store.store

        if args.msg_id in message_store:
            run_ctx.cli.set_message_ctx(message_store[args.msg_id])
