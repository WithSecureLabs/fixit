"""
cmd_history.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `History` command, which provides functionality
    for displaying and managing the FIX message history of a session.

    The `History` class extends the `Command` base class and allows users to:
    - LIST: Lists the session's message history.
    - VIEW: Displays the details of a specific history entry.
    - SAVE: Saves a history entry to a file for later use.

Usage:
    ```python
    history_cmd = History()
    history_cmd.run(cli=cli_instance, user_input="list")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *
from fixit.utils.common import *

from fixit.core.commands.history import *

__all__ = ["History"]

class History(Command):
    """
    A command to show the application's message history.

    The `History` command provides functionality for interacting with the message history
    within a FIX session. Users can list the entire message history, view details of a
    specific entry, or save an entry to a file for later use.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Displays the session's message history")
        self._init_arg_parser([
            {
                "name": "session_num",
                "data": {
                    "metavar": "[SESSION_NUM]",
                    "help": ARGS_SESSION_DESC,
                }
            },
            {
                "name": "action",
                "data": {
                    "help": ARGS_ACTION_DESC,
                    "choices": ["LIST", "VIEW", "SAVE"],
                    "type": str.upper,
                    "nargs": "?"
                }
            },
        ])
        self.set_example([
            "history              - List the latest message history ",
            "history list 20      - List the last 20 messages processed",
            "history view -1      - View the last message processed",
            "history view 12      - View the 12th message processed",
            "history view 12 RAW  - View the 12th message in it's raw format",
            "history save 10      - Save the 10th message processed to the message store",
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        actions = self.parser_args["action"].choices
        args, args_trail = self.parse_input(run_ctx, actions, auto_session=True)

        if args.action is None:
            self._history_list(run_ctx, args, user_input=args_trail)
            return

        # Run action history_<action>() function
        self.run_action(run_ctx, args, user_input=args_trail, prefix="_history_")


    def _history_list(self, run_ctx, args, user_input):
        """ Outputs the specified session's message history in table format """
        List(f"{self.name} list").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli,
        )


    def _history_view(self, run_ctx, args, user_input):
        """ View specific details of the session history """
        View(f"{self.name} view").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli,
        )


    def _history_save(self, run_ctx, args, user_input):
        """ Save a history entry to a file for later use """
        Save(f"{self.name} save").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli,
        )


