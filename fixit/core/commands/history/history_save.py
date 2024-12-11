"""
history_save.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Save` command, which provides functionality to save a specific
    FIX message from the session history to a file. Users can export messages in various formats,
    including binary, plain text, and XML, for further analysis or archival purposes.

Key Features:
    - Supports saving messages to disk in multiple formats:
        - Binary (default)
        - Text
        - XML
    - Generates default file names based on session and message IDs.
    - Handles file creation and ensures the message directory exists.

Usage:
    The `Save` command is executed to export a FIX message to a file. Example:
        ```python
        save_cmd = Save("history_save")
        save_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id=10, file_name="message.txt"
        )
        ```
    Arguments:
        - `msg_id`: The ID of the message to save (required).
        - `file_name`: The output file name, including extension (optional).
"""

from os import path
from os import makedirs

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Save(Command):
    """ Used to save a message to disk """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Saves a specified message to a file")
        self._init_arg_parser([
            {
                "name": "msg_id",
                "data": {
                    "metavar": "<MESSAGE ID>",
                    "help": "Comma separated message IDs to save",
                    "type": int
                }
            },
            {
                "name": "file_name",
                "data": {
                    "metavar": "[FILE_NAME]",
                    "help": "The output file name for the message",
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
        formats = ["bin", "txt", "xml"]
        file_format = formats[0]
        args, _ = self.parse_input(run_ctx)

        if args.file_name is None:
            args.file_name = self._gen_output_file_name(run_ctx, args.msg_id, file_format)

        else:
            file_format = args.file_name.split(".")[-1]

        message_log = run_ctx.cli.client.get_session_message_log(run_ctx.session_num)

        try:
            msg = message_log[args.msg_id]["msg"]

            if file_format == "bin":
                msg = run_ctx.cli.client.msg_to_str(msg, binary=True)

            if file_format == "xml":
                msg = run_ctx.cli.client.msg_to_xml(msg)

            status = self._write_to_file(run_ctx, args.file_name, msg)
            if status is True:
                run_ctx.cli.writer.info((
                    f"Message {run_ctx.session_num}[{args.msg_id}] "
                    f"written to file {args.file_name}"
                ))

        except (ValueError, IndexError):
            run_ctx.cli.writer.error("Invalid message ID")


    def _gen_output_file_name(self, run_ctx, msg_id, ext):
        """ Generate a file name for the message """
        return Utils.gen_file_name(f"msg-{run_ctx.session_num}-{msg_id}", ext)


    def _write_to_file(self, run_ctx, file_name, data):
        """ Writes the provided data to a file """
        if not path.isdir(MSG_DIR):
            makedirs(MSG_DIR)

        try:
            with open(f"{MSG_DIR}{file_name}", "ab") as f:
                f.write(bytes(data, F_ENCODING))
                f.write(b"\n")
                return True

        except (OSError, IOError):
            run_ctx.cli.writer.error(
                f"Could not write to file {file_name}"
            )

        return False
