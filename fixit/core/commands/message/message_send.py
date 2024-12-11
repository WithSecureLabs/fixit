"""
message_send.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Send` command, responsible for sending FIX messages
    over a specified session. The command provides flexibility to send messages
    in different modes, including raw and modified formats.

Key Features:
    - Retrieve messages from the context or message store for transmission.
    - Send messages in different formats:
        - Standard FIX message.
        - Raw FIX message.
        - Raw FIX message with updated SendingTime.
    - Supports test message sending to verify session connectivity and behavior.
    - Handles message modifiers to adjust the behavior of sent messages.

Usage:
    The `Send` command can be used to send messages via the current session. Example:
        ```python
        send_cmd = Send("message_send")
        send_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id="FIX.4.2:NEW_ORDER_D-D:1", modifier="RAW-UT"
        )
        ```

    Arguments:
        - `msg_id`: Specifies the identifier of the message to be sent.
        - `modifier`: Adjusts the sending behavior:
            - `RAW`: Sends the raw message data.
            - `RAW-UT`: Sends the raw message data with an updated SendingTime.
            - `TEST`: Sends a test message.
"""

import time

from argparse import REMAINDER

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.utils.exceptions import NoActiveMessageError

from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *


class Send(Command):
    """ Sends a FIX message over a specified session """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Sends a FIX message over a specified session")
        self._init_arg_parser([
            {
                "name": "msg_id",
                "data": {
                    "metavar": "[MESSAGE ID]",
                    "help": "The message store ID to view. Defaults to active message",
                }
            },
            {
                "name": "mode",
                "data": {
                    "help": "Optional modifier. Send a TEST or RAW message (RAW updates critical fields by default)",
                    "choices": ["TEST", "RAW"],
                    "type": str.upper,
                    "nargs": "?"
                }
            },
            {
                "name": "modifier",
                "data": {
                    "help": "RAW modifier: Precents update of SeqNum (-US) / BodyLength (-UL) / SendingTime (-UT) / Checksum (-UC)",
                    "metavar": "[-US|-UL|-UT|-UC]",
                    "type": str.upper,
                    "nargs": REMAINDER,
                }
            },
        ])
        self.set_example([
            "message send test        - Send a test message",
            "message send             - Send the active message",
            "message send RAW         - Send the current raw message (no protocol modifications)",
            "message send RAW -UT     - Send raw message without updating the SendingTime (52)",
            "message send RAW -UC     - Send raw message without updating the Checksum (10)",
            "message send RAW -US -UT - Send raw message without updating the MsgSeqNum (34) or SendingTime (52)",
        ])

    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx, auto_message=True)

        # If no message ID is used, check if in its place the keyword test is used
        # If so, send a test message and return
        if args.msg_id.upper() == "TEST":
            self._send_test(run_ctx)
            return

        message = self._get_message(run_ctx, args.msg_id)
        spec_str = None

        if len(args_trail) > 0:
            spec_str = args_trail[0].strip() if "FIX" in args_trail[0] else None

        message_raw = message['msg']
        if message is not None:
            message = run_ctx.cli.client.str_to_msg(message['msg'], spec_str=spec_str)

        else:
            return

        if args.mode == "RAW":
            self._send_raw_message(run_ctx, message_raw, args.mode, args.modifier)

        else:
            self._send_message(run_ctx, message)


    def _get_message(self, run_ctx, msg_id):
        """ Retrieves a message from the current context, or the message store """
        if run_ctx.cli.get_message_ctx() != {}:
            if msg_id == run_ctx.cli.get_message_ctx()["id"]:
                return run_ctx.cli.get_message_ctx()

        message_store = run_ctx.cli.message_store.store
        if msg_id in message_store:
            return message_store[msg_id]

        raise NoActiveMessageError()


    def _send_message(self, run_ctx, message):
        """ Send a specified message over the current session """
        run_ctx.cli.client.send_message(run_ctx.session_num, message)
        time.sleep(RESP_DELAY['value'])


    def _send_raw_message(self, run_ctx, message, mode, modifier):
        """ Send a raw message over the current session """
        if "-UT" not in modifier:
            message = Utils.msg_str_set_field(
                message, 52, str(Utils.gen_timestamp())
            )

        if "-US" not in modifier:
            message = Utils.msg_str_set_field(
                message, 34, str(run_ctx.cli.client.get_next_seq_num(run_ctx.session_num))
            )

        if "-UL" not in modifier:
            message = Utils.msg_str_set_field(
                message, 9, str(Utils.msg_str_calc_length(message))
            )

        if "-UC" not in modifier:
            message = Utils.msg_str_set_field(
                message, 10, str(Utils.msg_str_calc_chksum(message))
            )

        run_ctx.cli.client.send_raw_data(
            run_ctx.session_num, message, run_ctx, clean_up=False
        )
        time.sleep(RESP_DELAY['value'])


    def _send_test(self, run_ctx):
        """ Send a test message over the current session """
        run_ctx.cli.client.send_test_message(run_ctx.session_num)
        time.sleep(RESP_DELAY['value'])
