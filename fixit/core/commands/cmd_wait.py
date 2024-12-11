"""
cmd_wait.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Wait` command, which is used to make the
    application pause. This is typically used during command preloading

Usage:
    ```python
    wait_cmd = Wait()
    wait_cmd.run(cli=cli_instance, user_input="1")
    ```
"""

import time

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Wait"]

class Wait(Command):
    """
    A command to pause appliction command processing

    The `Wait` command facilitates the ability to make the application
    stop processing commands fot a predetermined period of time.
    This is typically used during command preloading.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Causes the application to wait for the supplied number of seconds")
        self._init_arg_parser([
            {
                "name": "seconds",
                "data": {
                    "metavar": "<SECONDS>",
                    "help": "Time in seconds to wait",
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
        args, args_trail = self.parse_input(run_ctx)

        try:
            args.seconds = abs(float(args.seconds))
        except ValueError:
            raise InvalidArgsError()

        run_ctx.cli.writer.info(f"Waiting {args.seconds} seconds...")
        time.sleep(args.seconds)
