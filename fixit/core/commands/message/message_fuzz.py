"""
message_fuzz.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Fuzz` command, which allows users to perform fuzz testing
    on specific message fields for a given (or active) message. It is designed to test
    the robustness of message processing by sending modified field values and analyzing
    responses.

Key Features:
    - Fuzzes specified fields of a FIX message with random or user-specified data.
    - Supports dictionary-based fuzzing for custom payloads.
    - Logs fuzzing results, including payloads, sent messages, and responses, to a CSV file.
    - Ensures critical fields like `BeginString`, `SenderCompID`, and `SendingTime` are not fuzzed.
    - Handles automatic updates to timestamps and sequence numbers.

Usage:
    The `Fuzz` command is executed to test FIX messages. Example:
        ```python
        fuzz_cmd = Fuzz("message_fuzz")
        fuzz_cmd.run(
            user_input=user_input, session_num=session, cli=run_ctx.cli,
            msg_id="FIX.4.2:NEW_ORDER_D-D:1", dict_file="fuzz_dict.txt",
            fields=["38", "44"]
        )
        ```
    Arguments:
        - `msg_id`: The ID of the message to fuzz (required).
        - `dict_file`: An optional file containing fuzzing payloads.
        - `fields`: A list of fields to fuzz.
"""

import time
import csv

from os import path
from os import makedirs

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *

class Fuzz(Command):
    """ Fuzz a message's fields """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Fuzz a message's fields")
        self._init_arg_parser([
            {
                "name": "msg_id",
                "data": {
                    "metavar": "[MESSAGE ID]",
                    "help": "The message store ID to fuzz. Defaults to active message",
                }
            },
            {
                "name": "dict_file",
                "data": {
                    "help": "Fuzzing data dictionary file",
                    "nargs": "?"
                }
            },
            {
                "name": "fields",
                "data": {
                    "metavar": "F1 F2 F3",
                    "help": "Fields to fuzz",
                    "nargs": "*"
                }
            }
        ])
        self.set_example([
            "message fuzz ../files/sqli.txt 55 - Fuzz based on a wordlist",
            "message fuzz 55 38                - Fuzz with generated data",
        ])


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        if len(run_ctx.user_input) <= 1:
            run_ctx.user_input.insert(0, "")

        if len(run_ctx.user_input) > 0 and not path.isfile(run_ctx.user_input[0]):
            run_ctx.cli.writer.warning(
                "No valid dict file provided, using generator"
            )
            run_ctx.user_input[0] = None

        args, _ = self.parse_input(run_ctx, auto_message=True)
        message_store = run_ctx.cli.message_store.store

        if args.msg_id in message_store:
            run_ctx.cli.set_message_ctx(message_store[args.msg_id])
            message = run_ctx.cli.get_message_ctx()["msg"]

            self._fuzz_message_fields(
                run_ctx, message, args.dict_file, args.fields
            )

        else:
            run_ctx.cli.writer.info(
                f"Unknown message: {args.msg_id}"
            )


    def _fuzz_message_fields(self, run_ctx, message, dict_file, fields):
        """ Fuzz message fields """
        run_ctx.cli.writer.info("Fuzzing message!")
        fuzz_dict = self._generate_fuzz_data(100)

        if dict_file is not None:
            fuzz_dict = self._load_dict_file(run_ctx, dict_file)

        if not path.isdir(OUT_DIR):
            makedirs(OUT_DIR)

        fuzz_out_file = f"{OUT_DIR}{self._gen_output_file_name(run_ctx, '.csv')}"

        with open(fuzz_out_file, "w", encoding=F_ENCODING) as csv_file:
            writer = csv.writer(csv_file, escapechar="\\")
            writer.writerow(["ID", "Payload", "Message", "Response"])

        counter = 0
        fuzz_delay = str(run_ctx.cli.get_option("fuzz_delay"))
        msg_str_orig = message

        for field in fields:
            if not self._valid_field(field):
                run_ctx.cli.writer.warning(f"Invalid field {field} - Skipping...")
                continue

            # TODO: Adapt fuzzing to work on critical fields
            for _val in fuzz_dict:
                message = msg_str_orig
                message = Utils.msg_str_set_field(
                    message, int(field), TARGET_FLAG # Isolate with flag
                )

                # Update message timestamp
                sending_time = Utils.gen_timestamp()
                message = Utils.msg_str_set_field(message, 52, sending_time)

                # Replace flag with value # Note checksum and length will be updated automatically
                message = message.replace(TARGET_FLAG, Utils.bytes_to_ascii(_val))

                # Track changes
                run_ctx.cli.client.set_editedMessageFlag(run_ctx.session_num, True)
                run_ctx.cli.client.set_editedMessage(run_ctx.session_num, message)

                # Send raw data to the acceptor and read the response
                run_ctx.cli.client.send_message(run_ctx.session_num, message)

                attempts = 0
                response = ""

                while attempts < 10:
                    # Retrieve last message from session histroy
                    last_message = run_ctx.cli.client.get_session_message_log(
                        run_ctx.session_num, depth=1
                    )[0]["msg"]

                    # If the last message is not the message sent, then it is the last response
                    if sending_time not in last_message:
                        response = last_message
                        break

                    time.sleep(FUZZ_DELAY['value'])

                with open(fuzz_out_file, "a", encoding=F_ENCODING) as csv_file:
                    writer = csv.writer(csv_file, escapechar="\\", quotechar='"', quoting=csv.QUOTE_ALL)
                    writer.writerow([
                        counter,
                        Utils.bytes_to_ascii(_val, True).replace(b"\n",b"\\n"),
                        Utils.bytes_to_ascii(message, True).replace(b"\n",b"\\n"),
                        Utils.bytes_to_ascii(response, True).replace(b"\n",b"\\n")
                    ])

                counter += 1
                time.sleep(float(fuzz_delay))

        run_ctx.cli.writer.info(f"\nFuzz output saved to: {fuzz_out_file}...")


    def _valid_field(self, field):
        """ Retursn True if a field is valid, False if not  """
        invalid_fields = [
            8,  # BeginString
            49, # SenderCompID
            56, # TargetCompID
            52  # SendimgTime
        ]

        return int(field) not in invalid_fields


    def _gen_output_file_name(self, run_ctx, ext):
        """ Generate a file name for the fuzzing output """
        return Utils.gen_file_name(f"fuzz-{run_ctx.session_num}", ext)


    def _generate_fuzz_data(self, n=128):
        """ Generates a list of random binary data """
        values_list = []
        for _val in range(n):
            if chr(_val) not in [SOH_UNI['value'], SOH_BIN, DELIM_UNI, DELIM_BIN]:
                values_list.append(chr(_val))

        return values_list


    def _load_dict_file(self, run_ctx, file_name):
        """ Loads fuzzing data from a specified file """
        values_list = []
        try:
            with open(file_name, "rb") as f:
                for line in f.readlines():
                    values_list.append(line)

        except (OSError, IOError):
            run_ctx.cli.writer.error(
                f"Could not read file {file_name}"
            )

        return values_list
