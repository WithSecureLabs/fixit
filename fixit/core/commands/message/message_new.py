"""
message_new.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `New` command, which allows users to quickly create
    new FIX message templates from a predefined set of message types.

Key Features:
    - Provides a selection of predefined message templates (e.g., orders, market data subscriptions).
    - Automatically generates unique message IDs for each new message.
    - Supports interactive creation and customization of messages.
    - Integrates with the message store to persist newly created messages.
    - Allows seamless integration with other commands, such as saving messages to disk.

Usage:
    The `New` command is used to create and initialize FIX messages for various purposes. Example:
        ```python
        new_cmd = New("message_new")
        new_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli, source="ORD-BUY"
        )
        ```
    Arguments:
        - `source`: Specifies the type of FIX message to create, such as:
            - `FREE`: Free-form message.
            - `TEST`: Test message.
            - `ORD-BUY`: New order for buying.
            - `ORD-SELL`: New order for selling.
            - `MD-SUB`: Market data subscription.
            - `MD-SUB-CANCEL`: Market data subscription cancellation.
            - `ORD-CANCEL`: Order cancellation.
            - `ORD-STAT`: Order status request.
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

from fixit.core.commands.message import Save

class New(Command):
    """ Used to save a message to disk """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Creates a new message")
        self._init_arg_parser([
            {
                "name": "source",
                "data": {
                    "help": "The type of message to create",
                    "choices": [
                        "FREE", "TEST",
                        "ORD-BUY", "ORD-SELL",
                        "MD-SUB", "MD-SUB-CANCEL",
                        "ORD-CANCEL", "ORD-STAT"
                    ],
                    "type": str.upper,
                }
            },
        ])
        self.set_example([
            "message new ORD-BUY",
            "message new ORD-CANCEL 12",
            "message send raw",
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        sources = self.parser_args["source"].choices

        if len(run_ctx.user_input) == 0 or run_ctx.user_input[0].upper() not in sources:
            run_ctx.user_input.insert(0, sources[0])

        args, args_trail = self.parse_input(run_ctx)

        msg = run_ctx.cli.client.create_message(
            run_ctx.session_num, args.source, user_input=args_trail
        )

        if msg is None:
            return

        store_id = run_ctx.cli.message_store.gen_MsgStoreID(run_ctx.cli, msg)
        msg_type, msg_type_name = run_ctx.cli.client.get_message_type(msg)

        msg_obj = {
            "id"   : store_id,
            "type" : f"{msg_type} ({msg_type_name})",
            "msg"  : run_ctx.cli.client.msg_to_str(msg)
        }

        run_ctx.cli.set_message_ctx(msg_obj)

        Save(f"{self.name} save").run(
            user_input = "",
            session_num = run_ctx.session_num,
            cli = run_ctx.cli
        )
