"""
message_load.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Load` command, which enables users to load FIX messages
    into the application’s message store. Messages can be loaded either from raw string
    input or from a file containing FIX messages (including text, bin, or pcapng files).

Key Features:
    - Supports loading messages from raw strings or files.
    - Parses and validates FIX messages before adding them to the store.
    - Handles standard FIX message formatting, including delimiters and required fields.
    - Automatically replaces session-specific identifiers (e.g., SenderCompID, TargetCompID)
      during message loading.
    - Provides regex-based parsing for extracting FIX messages from files.

Usage:
    The `Load` command is used to import FIX messages into the message store. Example:
        ```python
        load_cmd = Load("message_load")
        load_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            source="FILE", message="fix_capture.pcapng"
        )
        ```
    Arguments:
        - `source`: Specifies the source of the message (`FILE` or `STRING`).
        - `message`: The raw message string or file path containing FIX messages.
"""

import re

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Load(Command):
    """ Used to save a message to disk """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Loads a message into the application")
        self._init_arg_parser([
            {
                "name": "source",
                "data": {
                    "help": "Defines the loading source",
                    "choices": ["FILE", "STRING"],
                    "type": str.upper,
                    "nargs": "?"
                }
            },
            {
                "name": "message",
                "data": {
                    "metavar": "<MESSAGE>",
                    "help": "The raw message string input or file name",
                }
            },
        ])
        self.set_example([
            "message load FILE ./messages/fix_capture.pcapng YES_ALL   - load from file",
            "message load STRING '8=FIX.4.2|9=146|35=D|34=15|49=[...]' - Fuzz with generated data",
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        sources = self.parser_args["source"].choices
        args, args_trail = self.parse_input(run_ctx)

        if args.source is None:
            args.source = sources[0]

        args.action = args.source

        # Else, run action load_from_<action>() function
        self.run_action(run_ctx, args, user_input=args_trail, prefix="load_from_")


    def load_from_string(self, run_ctx, args, user_input):
        """ Loads a message into the message store based on a provide string """
        msg = run_ctx.cli.client.str_to_msg(args.message)
        if msg is None:
            return

        run_ctx.cli.message_store.update_store(run_ctx.cli, msg, user_input=user_input)


    def load_from_file(self, run_ctx, args, user_input):
        """ Parses a given file and extracts any FIX messages within it """
        file_name = args.message
        msg_regex = r"^.*(8=FIX.*(?:\\x01|\|)10=[0-9]{3}(?:\\x01|\|)).*$"

        messages = {}
        try:
            with open(file_name, "rb") as f:

                for line in f.readlines():

                    if not str(line).startswith("#"):
                        match = re.search(msg_regex, str(line))

                        if match:
                            message = {}
                            msg_str = match.group(1)
                            m_key = ""
                            msg_str = msg_str.replace("\\x01", SOH_UNI['value'])

                            for field in msg_str.split(SOH_UNI['value']):
                                field = field.strip()
                                if field == "":
                                    continue
                                k, v = field.split("=", 1)

                                if k == "49":
                                    v = run_ctx.cli.client.get_session_config(
                                        "SenderCompID", run_ctx.session_num
                                    )
                                if k == "56":
                                    v = run_ctx.cli.client.get_session_config(
                                        "TargetCompID", run_ctx.session_num
                                    )

                                message[k] = v
                                m_key += k

                            # Add the message to the list of messages
                            # Using the combination of fields as the signature
                            messages[m_key] = message

        except (OSError, IOError):
            run_ctx.cli.writer.error(
                f"Could not read file {file_name}"
            )
            return

        for m_key, msg in messages.items():
            msg_str = ""
            for k,v in msg.items():
                msg_str += k + "=" + v + SOH_UNI['value']
            msg_str = msg_str.replace(SOH_BIN, SOH_UNI['value']).strip()

            args.message = msg_str
            self.load_from_string(run_ctx, args, user_input)

        run_ctx.cli.message_store.auto_resp = None
