"""
message_view.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `View` command, providing functionality to view detailed the
    specific FIX message stored in the application. It supports multiple formats for
    displaying message details, such as raw, type, and expanded dictionary views.

Key Features:
    - Retrieves a specific FIX message by its unique identifier.
    - Displays the message in raw format, expanded dictionary view, or shows its type.
    - Supports user-defined dictionaries for expanded views.

Usage:
    The `View` command is designed to allow users to inspect the contents and metadata
    of FIX messages for debugging or analysis. Example:
        ```python
        view_cmd = View("message_view")
        view_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id="FIX.4.2:NEW_ORDER_D-D:1", action="RAW"
        )
        ```

    Arguments:
        - `msg_id`: Specifies the identifier of the message to be viewed.
        - `action`: Defines how the message should be displayed (RAW, TYPE, DICT).
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class View(Command):
    """ Sets the value of a key """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Views the message information of a given message ID")
        self._init_arg_parser([
            {
                "name": "msg_id",
                "data": {
                    "metavar": "<MESSAGE ID>",
                    "help": "The message store ID to view",
                }
            },
            {
                "name": "action",
                "data": {
                    "help": ARGS_ACTION_DESC,
                    "choices": ["RAW", "TYPE", "FILTER"],
                    "type": str.upper,
                    "nargs": "?"
                }
            },
        ])
        self.set_example([
            "message view                     - View the active message",
            "message view type                - View the active message type",
            "message view raw                 - View the message in raw format",
            "message view FILTER '.*Symbol.*' - View a specific value in the message"
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        actions = self.parser_args["action"].choices
        args, args_trail = self.parse_input(run_ctx, actions, auto_message=True)

        if args.action is None:
            self._view_message(run_ctx, args, user_input=args_trail)
            return

        self.run_action(run_ctx, args, user_input=args_trail, prefix="_view_")


    def _get_message(self, run_ctx, msg_id):
        """ Retrieves a message from the current context, or the message store """
        if run_ctx.cli.get_message_ctx() != {}:
            if msg_id == run_ctx.cli.get_message_ctx()["id"]:
                return run_ctx.cli.get_message_ctx()["msg"]

        message_store = run_ctx.cli.message_store.store
        if msg_id in message_store:
            return message_store[msg_id]["msg"]

        return None


    def _view_message(self, run_ctx, args, user_input):
        """ Prints the full message as specified by a provided message ID """
        filter = ".*" if len(user_input) == 0 else user_input[0]
        Utils.message_expand(run_ctx, self._get_message(run_ctx, args.msg_id), filter=filter)


    def _view_filter(self, run_ctx, args, user_input):
        self._view_message(run_ctx, args, user_input)


    def _view_raw(self, run_ctx, args, user_input):
        """ Describes each message field for a specific message using its history ID """
        Utils.message_view(run_ctx, self._get_message(run_ctx, args.msg_id))


    def _view_type(self, run_ctx, args, user_input):
        """ Prints the MsgType value for the specified message """
        Utils.message_get_type(run_ctx, self._get_message(run_ctx, args.msg_id))
