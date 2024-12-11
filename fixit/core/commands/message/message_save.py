"""
message_save.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Save` command, which is responsible for saving the
    current state of a FIX message into the message store. It ensures that messages
    are properly validated and stored with a unique identifier.

Key Features:
    - Supports saving messages with custom or default identifiers.
    - Validates the message before saving to ensure consistency.
    - Updates the message context after successful saving for seamless interaction.
    - Allows integration with other commands to manage the message lifecycle effectively.

Usage:
    The `Save` command can be used to save the current message state into the store. Example:
        ```python
        save_cmd = Save("message_save")
        save_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            store_id="custom_id"
        )
        ```

    Arguments:
        - `store_id`: (Optional) Specifies a custom identifier for the message in the store.
                      If not provided, the existing message ID is used.
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Save(Command):
    """ Sets the value of a key """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Save the current message to the message store")
        self._init_arg_parser([
            {
                "name": "store_id",
                "data": {
                    "metavar": "[STORE_ID]",
                    "help": "The new name to save the message as",
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
        args, _ = self.parse_input(run_ctx)

        message = run_ctx.cli.get_message_ctx()
        if message == {}:
            return

        if args.store_id is None:
            args.store_id = message["id"]

        store_id = self._save_message(run_ctx, message["msg"], args.store_id)

        if store_id is None:
            return

        message_store = run_ctx.cli.message_store.store
        run_ctx.cli.set_message_ctx(message_store[store_id])


    def _save_message(self, run_ctx, message, store_id):
        """ Saves the current context message to the message store """
        msg = run_ctx.cli.client.str_to_msg(message)
        if msg is None:
            run_ctx.cli.writer.error(
                "Cannot save invalid message"
            )
            return None

        store_id = run_ctx.cli.message_store.update_store(run_ctx.cli, msg, store_id=store_id)
        run_ctx.cli.writer.info(
            f"Message saved: {store_id}"
        )

        return store_id
