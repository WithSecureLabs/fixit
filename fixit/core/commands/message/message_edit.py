"""
message_edit.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Edit` command, which allows users to modify FIX messages in the
    message store. It supports both interactive editing through a text editor and automated
    field-value updates via commands.

Key Features:
    - Interactive Editing:
        - Opens messages in a text editor for field-by-field modifications.
    - Command-Based Editing:
        - Updates specific fields directly through provided arguments.
    - Field Expansion and Compression:
        - Expands FIX messages into readable field-value pairs for editing.
        - Compresses modified fields back into a valid FIX message string.
    - Validation:
        - Validates the edited message to ensure it conforms to the FIX format.

Usage:
    The `Edit` command is executed to modify a message by its store ID. Example:
        ```python
        edit_cmd = Edit("message_edit")
        edit_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id="FIX.4.2:NEW_ORDER_D-D:1", fields=["38=500", "44=32.09"]
        )
        ```
    Arguments:
        - `msg_id`: The ID of the message to edit (required).
        - `fields`: A list of field-value pairs to update (optional).
"""

import click
from colorama import Fore

from argparse import REMAINDER

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *


class Edit(Command):
    """ Edits the specified FIX message """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Edit the active message, or one specified by message ID")
        self._init_arg_parser([
            {
                "name": "msg_id",
                "data": {
                    "metavar": "[MESSAGE ID]",
                    "help": "The message store ID to edit. Defaults to active message",
                }
            },
            {
                "name": "fields",
                "data": {
                    "metavar": "[F1=V1] [-F3]",
                    "help": "Field-value pairs to insert, update, remove",
                    "nargs": REMAINDER
                }
            }
        ])
        self.set_example([
            "message edit              - Freely edit message",
            "message edit 55=TEST      - Set field 55 = 'TEST'",
            "message edit +13:44=70.00 - Insert field 55=70.00 at position 13",
            "message edit -44          - Remove field 44",
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx, auto_message=True)
        message_store = run_ctx.cli.message_store.store

        if args.msg_id in message_store:
            run_ctx.cli.set_message_ctx(message_store[args.msg_id])

            message = run_ctx.cli.get_message_ctx()["msg"]

            if len(args.fields) > 0:
                new_message = self._auto_edit_message_fields(
                    run_ctx, message, args.fields
                )

            else:
                new_message = self._edit_message_fields(run_ctx, message)

            run_ctx.cli.client.set_editedMessageFlag(run_ctx.session_num, True)
            run_ctx.cli.client.set_editedMessage(run_ctx.session_num, new_message)

            run_ctx.cli.get_message_ctx()["msg"] = new_message

        else:
            run_ctx.cli.writer.info(
                f"Unknown message: {args.msg_id}"
            )


    def _auto_edit_message_fields(self, run_ctx, message_orig, message_ops):
        """ Automaticaly edit message fields based on provided key=value pairs """
        msg_obj = message_orig # run_ctx.cli.client.str_to_msg(message_orig)
        if msg_obj is None:
            return message_orig

        for field in message_ops:
            try:
                if field.startswith("-"):
                    f_num = int(field[1::])
                    msg_obj = Utils.msg_str_remove_field(msg_obj, f_num)
                    run_ctx.cli.writer.info(
                        f"Message updated: {f_num} removed"
                    )

                elif field.startswith("+"):
                    f_pos, f_data = field.split(":", 1)
                    f_num, f_value = f_data.split("=", 1)
                    msg_obj = Utils.msg_str_insert_field(msg_obj, f_pos, f_num, f_value)
                    run_ctx.cli.writer.info(
                        f"Message updated: Inserted {f_num}={f_value} @ pos {f_pos}"
                    )

                else:
                    f_num, f_value = field.split("=", 1)
                    msg_obj = Utils.msg_str_set_field(msg_obj, int(f_num), str(f_value))
                    run_ctx.cli.writer.info(
                        f"Message updated: {f_num}={f_value}"
                    )

            except (ValueError, TypeError) as e:
                run_ctx.cli.writer.warning(
                    f"Invalid field: {field} - skipping"
                )
                continue

        #return run_ctx.cli.client.msg_to_str(msg_obj)
        return msg_obj


    def _edit_message_fields(self, run_ctx, message_orig):
        """ Interactively edit message fields """
        expanded = True
        message = self._expand_message(
            run_ctx, message_orig
        )

        if message is None:
            message = message_orig
            expanded = False

            warning = "Unable to expand fields! Opening raw message [ENTER]: "
            warning = run_ctx.cli.writer.categorise(warning, cat="WARNING")
            warning = run_ctx.cli.writer.colour(warning, Fore.YELLOW)

            run_ctx.cli.writer.prompt(warning)

        # Open the expanded message in a text editor for editing
        # Select an editor.  To change later, run 'select-editor'.
        new_message = click.edit(message)

        # If message was unaltered, return
        if new_message is None:
            return message_orig

        # Compress the expanded message back to a FIX message str
        if expanded:
            new_message = self._compress_message(run_ctx, new_message)

        # If not compressed, remove trailing new line
        else:
            new_message = new_message.replace("\n", "")

        # Validate the message by converting it to a FIX message object
        msg_obj = run_ctx.cli.client.str_to_msg(new_message)

        # If message conversion failed, return message string
        if msg_obj is None:
            run_ctx.cli.writer.warning(
                "Message updated failed!"
            )
            return message_orig

        # Else, Save the new message changes in the message context incase validation fails
        run_ctx.cli.get_message_ctx()["msg"] = new_message
        message = run_ctx.cli.client.msg_to_str(msg_obj)

        run_ctx.cli.writer.info(
            "Message updated!"
        )

        return message


    def _expand_message(self, run_ctx, message):
        """ Describes each message field for a specific message using its history ID """
        message_fields = run_ctx.cli.client.msg_expand(message)
        if len(message_fields) == 0:
            return None

        field_str = ""
        for field in message_fields:
            field_str += f"{field['field_num']}({field['field_name']})={field['field_val']}\n"

        return field_str


    def _compress_message(self, run_ctx, message):
        """ Collapse an expanded message back into a standard FIX structure """
        messge_str = ""
        for row in message.split("\n"):

            if len(row.strip()) == 0:
                continue

            # Try to compress the field
            try:
                num, val = row.split("=", 1)
                num = num.split("(")[0]
                messge_str += f"{num}={val}{SOH_UNI['value']}"

            except ValueError:
                run_ctx.cli.writer.error(
                    f"Invalid field: '{row}'"
                )

                # Prompt to edit the message
                error = "Press ENTER to amend or type 'REMOVE': "
                error = run_ctx.cli.writer.categorise(error, cat="WARNING")
                error = run_ctx.cli.writer.colour(error, Fore.YELLOW)
                option = run_ctx.cli.writer.prompt(error)

                # If the user input was "R" or "Remove"
                if len(option) > 0 and option[0].upper().startswith("R"):
                    run_ctx.cli.writer.warning(
                        f"Field removed: '{row}'"
                    )

                # Else, re-edit the message
                else:
                    new_message = click.edit(message)
                    if new_message is None:
                        new_message = message

                    return self._compress_message(run_ctx, new_message)


        return messge_str
