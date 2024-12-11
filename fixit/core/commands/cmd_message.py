"""
cmd_message.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Message` command, which provides functionality for
    creating, modifying, managing, and sending FIX messages.

    The `Message` class extends the `Command` base class and allows users to:
    - LIST: Displays all messages in the message store.
    - LOAD: Loads a specific message from a file or string.
    - VIEW: Displays a breakdown of the active message.
    - NEW: Creates a new message.
    - USE: Selects the specified message for editing and further use.
    - EDIT: Modifies the active message.
    - SAVE: Saves changes to the current message.
    - DELETE: Deletes a message from the message store.
    - SEND: Sends a message to the FIX session.
    - DROP: Discards the currently active message.
    - FUZZ: Allows for fuzzing of message fields.

Usage:
    ```python
    message_cmd = Message()
    message_cmd.run(cli=cli_instance, user_input="new ORD-BUY")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

from fixit.core.commands.message import *

__all__ = ["Message"]

class Message(Command):
    """
    A command to manage and interact with FIX messages.

    The `Message` command provides functionality for creating, modifying, managing,
    and sending FIX messages. It allows users to perform various actions on messages
    stored within the application.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Invoke message actions")
        self._init_arg_parser([
            {
                "name": "session_num",
                "data": {
                    "metavar": "[SESSION_NUM]",
                    "help": "The session name to retrieve message history from",
                }
            },
            {
                "name": "action",
                "data": {
                    "help": ARGS_ACTION_DESC,
                    "choices": [
                        "LIST", "LOAD", "VIEW",
                        "NEW", "USE", "DROP",
                        "EDIT", "SAVE", "DELETE",
                        "SEND", "FUZZ",
                    ],
                    "type": str.upper,
                    "nargs": "?"
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
        args, args_trail = self.parse_input(run_ctx, actions, auto_session=True)

        if args.action is None:
            self._message_list(run_ctx, args, user_input=args_trail)
            return

        # Else, run action message_<action>() function
        try:
            self.run_action(run_ctx, args, user_input=args_trail, prefix="_message_")
        except NoActiveMessageError as e:
            run_ctx.cli.writer.warning("No active message!")


    def _message_list(self, run_ctx, args, user_input):
        """ Executes the message_list sub-command """
        List(f"{self.name} list").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_load(self, run_ctx, args, user_input):
        """ Executes the message_load sub-command """
        Load(f"{self.name} load").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_view(self, run_ctx, args, user_input):
        """ Executes the message_view sub-command """
        View(f"{self.name} view").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_new(self, run_ctx, args, user_input):
        """ Executes the message_new sub-command """
        New(f"{self.name} new").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_use(self, run_ctx, args, user_input):
        """ Executes the message_use sub-command """
        Use(f"{self.name} use").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )

    def _message_edit(self, run_ctx, args, user_input):
        """ Executes the message_edit sub-command """
        Edit(f"{self.name} edit").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_save(self, run_ctx, args, user_input):
        """ Executes the message_save sub-command """
        Save(f"{self.name} save").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_delete(self, run_ctx, args, user_input):
        """ Executes the message_delete sub-command """
        Delete(f"{self.name} del").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_send(self, run_ctx, args, user_input):
        """ Executes the message_send sub-command """
        Send(f"{self.name} send").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )


    def _message_drop(self, run_ctx, args, user_input):
        """ Executes the message_drops sub-command """
        Drop(f"{self.name} drop").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )

    def _message_fuzz(self, run_ctx, args, user_input):
        """ Executes the message_fuzz sub-command """
        Fuzz(f"{self.name} fuzz").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )
