"""
history_view.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `View` command, which allows users to view detailed
    information about specific FIX messages from the session history. It supports
    multiple viewing options, such as raw message output, message type inspection,
    and expanded field descriptions.

Key Features:
    - View message fields in a human readable format.
    - Display raw FIX messages.
    - Inspect message types with categorized output.
    - Supports optional actions for customizing the view:
        - `RAW`: Displays the raw FIX message.
        - `TYPE`: Prints the message type and name.
        - `DICT`: Expands message fields for inspection.

Usage:
    The `View` command is executed to inspect FIX messages in various formats. Example:
        ```python
        view_cmd = View("history_view")
        view_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id=10, action="RAW"
        )
        ```
    Arguments:
        - `msg_id`: The ID of the message to view (required).
        - `action`: Optional action to specify the output format (`RAW`, `TYPE`, or `DICT`).
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
                    "help": "The message history ID to view",
                    "type": int
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
            "history view 1                         - Inspect the 1st message in the history",
            "history view -1                        - Inspect the last message in the history",
            "history view -2                        - Inspect the penultimate message in the history",
            "history view 5 raw                     - Inspect the 5th message in the history in raw format",
            "history view -1 type                   - Inspect the type of the last message in the history",
            "history view -1 FILTER '.*OrdStatus.*' - Search for a specific value in the message entry",
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
            self._view_message(run_ctx, args, user_input=args_trail)
            return

        # Run action message_<action>() function
        self.run_action(run_ctx, args, user_input=args_trail, prefix="_view_")


    def _view_message(self, run_ctx, args, user_input):
        """ Describes each message field for a specific message using its history ID """
        message_log = run_ctx.cli.client.get_session_message_log(run_ctx.session_num)
        filter = ".*" if len(user_input) == 0 else user_input[0]
        try:
            Utils.message_expand(run_ctx, message_log[args.msg_id]["msg"], filter=filter)
        except IndexError:
            pass


    def _view_filter(self, run_ctx, args, user_input):
        """ Views the message is an expanded key=value pair format """
        self._view_message(run_ctx, args, user_input)


    def _view_raw(self, run_ctx, args, user_input): #pylint: disable=unused-argument
        """ Prints the full message as specified by a provided history ID """
        message_log = run_ctx.cli.client.get_session_message_log(run_ctx.session_num)
        try:
            Utils.message_view(run_ctx, message_log[args.msg_id]["msg"])
        except IndexError:
            pass


    def _view_type(self, run_ctx, args, user_input): #pylint: disable=unused-argument
        """ Prints the MsgType value for the specified message """
        message_log = run_ctx.cli.client.get_session_message_log(run_ctx.session_num)
        try:
            Utils.message_get_type(run_ctx, message_log[args.msg_id]["msg"])
        except IndexError:
            pass
