#!/usr/bin/python3

"""
initiator.py - Part of the Fixit Project

Fixit v0.1 BETA
Author: Oliver Simonnet (@AppSecOllie)
Released as open source by WithSecure Labs (c) 2024
See LICENSE for more details.

The application enables users to interact with FIX gateways, send and manipulate FIX messages,
without being restricted to standard FIX specification requirements.

This product includes software developed by the QuickFIX project (http://www.quickfixengine.org/).

Description
    This module serves as the main entry point for the Fixit application. It is responsible
    for parsing initial command-line arguments, setting up application options, and starting
    an instance of the `FixitCli` class to run the interactive FIX client.
"""

import sys
import argparse
import quickfix as fix

from os import path

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.cli import FixitCli
from fixit.core.constants import *


def file_exists(file_path):
    """ Check if s file exists or not """
    if not path.isfile(file_path):
        raise argparse.ArgumentTypeError(f"The file '{file_path}' does not exist.")
    return file_path


def get_options():
    """ Defines the application's configurable options. """
    return {
        "config_file": {
            OPT_VAL: "./config/initiator.cfg",
            OPT_DESC: "FIX initiator configuration file"
        },
        "session": {
            OPT_VAL: "0",
            OPT_DESC: "The default FIX session to interact with"
        },
        "username": {
            OPT_VAL: "",
            OPT_DESC: "FIX session username for authentication"
        },
        "password": {
            OPT_VAL: "",
            OPT_DESC: "FIX session password for authentication"
        },
        "newpassword": {
            OPT_VAL: "",
            OPT_DESC: "New password for FIX session"
        },
        "message_store": {
            OPT_VAL: None,
            OPT_DESC: "Message store file, containing sample messages"
        },
        "verbose": {
            OPT_VAL: False,
            OPT_DESC: "Increase verbosity"
        },
        "seq_seed": {
            OPT_VAL: "",
            OPT_DESC: "Initial value for message sequence number"
        },
        "exp_seq_seed": {
            OPT_VAL: "",
            OPT_DESC: "Initial value for the next expected message sequence number"
        },
        "log_heartbeat": {
            OPT_VAL: False,
            OPT_DESC: "Log heartbeat messages by default"
        },
        "fuzz_delay": {
            OPT_VAL: "0.05",
            OPT_DESC: "Set the delay between fuzzing messages"
        },
        "resp_delay": {
            OPT_VAL: "0.1",
            OPT_DESC: "The time to wait for a FIX response"
        },
        "fix_delim": {
            OPT_VAL: "|",
            OPT_DESC: "The delimiter used for FIX message fields"
        },
    }


def parse_args():
    """ Parse the supplied command-line arguments """
    options = get_options()

    parser = argparse.ArgumentParser(
        description=DESCRIPTON, epilog=EXAMPLE,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {VERSION}"
    )

    # Positional arguments
    parser.add_argument(
        "config", metavar="<CONFIG_FILE>", default=options["config_file"][OPT_VAL],
        help=options["config_file"][OPT_DESC], type=file_exists
    )

    # Group: Session Configuration
    session_group = parser.add_argument_group("Session Configuration")

    session_group.add_argument(
        "-s", "--session", metavar="<DEFAULT_SESS>", default=options["session"][OPT_VAL],
        help=options["session"][OPT_DESC],
        required=False,
    )
    session_group.add_argument(
        "-u", "--username", metavar="<USERNAME>", default=options["username"][OPT_VAL],
        help=options["username"][OPT_DESC],
        required=False,
    )
    session_group.add_argument(
        "-p", "--password", metavar="<PASSWORD>", default=options["password"][OPT_VAL],
        help=options["password"][OPT_DESC],
        required=False,
    )
    session_group.add_argument(
        "-n", "--newpassword", metavar="<NEW PASSWORD>", default=options["newpassword"][OPT_VAL],
        help=options["newpassword"][OPT_DESC],
        required=False,
    )

    # Group: Message Handling
    message_group = parser.add_argument_group("Message Handling")
    message_group.add_argument(
        "-d", "--fix_delim", metavar="<FIX_DELIM>", default=options["fix_delim"][OPT_VAL],
        help=options["fix_delim"][OPT_DESC],
        required=False,
    )
    message_group.add_argument(
        "-S", "--store", metavar="<MESSAGE_STORE>", default=options["message_store"][OPT_VAL],
        help=options["message_store"][OPT_DESC],
        required=False,
    )
    message_group.add_argument(
        "-q", "--seq_seed", default=None,
        help=options["seq_seed"][OPT_DESC]
    )
    message_group.add_argument(
        "-x", "--exp_seq_seed", default=None,
        help=options["seq_seed"][OPT_DESC]
    )

    # Group: Fuzzing
    fuzzing_group = parser.add_argument_group("Fuzzing")
    fuzzing_group.add_argument(
        "-f", "--fuzz_delay", default=options["fuzz_delay"][OPT_VAL],
        help=options["fuzz_delay"][OPT_DESC]
    )
    fuzzing_group.add_argument(
        "-r", "--resp_delay", default=options["resp_delay"][OPT_VAL],
        help=options["resp_delay"][OPT_DESC]
    )

    # Group: Console Output
    console_group = parser.add_argument_group("Console Output")
    console_group.add_argument(
        "--colour", action="store_true", default=False,
        help="enables coloured console output"
    )
    console_group.add_argument(
        "--log_heartbeat", action="store_true", default=False,
        help=options["log_heartbeat"][OPT_DESC]
    )
    console_group.add_argument(
        "--verbose", action="store_true", default=False,
        help=options["verbose"][OPT_DESC]
    )

    # Group: Preloaded Commands
    preload_group = parser.add_argument_group("Preloaded Commands")
    preload_group.add_argument(
        "-P", "--preload", default=[],
        help="predefined commands to run on startup",
        nargs="*"
    )

    return parser.parse_args()


def run_fixit_cli(args, options):
    """ Runs the Fixit CLI application """
    try:
        cli = FixitCli(args, options)
        cli.start()
        cli.run()

    except (fix.ConfigError, fix.RuntimeError) as error:
        print(error)


def main():
    """ Main entry point of the application """
    try:
        options = get_options()
        args = parse_args()
        run_fixit_cli(args, options)
    except argparse.ArgumentTypeError as e:
        sys.stderr.write(f"Argument Error: {e}\n")
        sys.exit(1)



if __name__ == '__main__':
    main()
