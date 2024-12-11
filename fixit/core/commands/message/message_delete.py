"""
message_delete.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Delete` command, which provides functionality for deleting
    messages from the application message store. It allows users to specify a message
    by its store ID and confirm its deletion interactively.

Key Features:
    - Deletes a specified message from the message store by its store ID.
    - Interactive confirmation prompt to prevent accidental deletions.
    - Provides user feedback on the success or failure of the deletion operation.

Usage:
    The `Delete` command is executed to remove a message from the store. Example:
        ```python
        delete_cmd = Delete("message_delete")
        delete_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            store_id="FIX.4.2:NEW_ORDER_D-D:1"
        )
        ```
    Arguments:
        - `store_id`: The ID of the message to delete (required).
"""

from colorama import Fore

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Delete(Command):
    """ Deletes a specific message from the message store """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Deletes a message from the message store")
        self._init_arg_parser([
            {
                "name": "store_id",
                "data": {
                    "metavar": "<STORE_ID>",
                    "help": "The new name to save the message as",
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
        message_store = run_ctx.cli.message_store.store

        if args.store_id in message_store:
            warning = f"Delete {args.store_id}? [Yes/No]: "
            warning = run_ctx.cli.writer.categorise(warning, cat="WARNING")
            warning = run_ctx.cli.writer.colour(warning, Fore.YELLOW)

            # Continue to prompt the user until a correct options is provided
            response = args_trail[0].upper()

            while response not in ["YES", "NO"]:
                response = run_ctx.cli.writer.prompt(warning)[0].upper().strip()

            if response == "YES":
                run_ctx.cli.message_store.remove(args.store_id)
                run_ctx.cli.writer.warning(f"{args.store_id} Deleted!")
                return

            if response == "NO":
                return
        else:
            run_ctx.cli.writer.error(f"{args.store_id} not found")
