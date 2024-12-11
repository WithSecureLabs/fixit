"""
cmd_exit.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Exit` command, which allows for the graceful termination
    of the application.

Usage:
    ```python
    exit_cmd = Exit()
    exit_cmd.run(cli=cli_instance, user_input="")
    ```
"""
import sys

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Exit"]

class Exit(Command):
    """
    A command to clear the CLI interface of acticity.

    The `Exit` command is used to terminate the Fixit application.
    This logs off any sessions, and terminates the FIX initiator and interceptor.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Exits the applications")
        self._init_arg_parser()


    def run(self, **run_ctx):
        """
        Executes the command implementation.

        Args:
            run_ctx (dict): The runtime context containing the user input string and CLI instance.
        """
        run_ctx = SimpleNamespace(**run_ctx)
        args, args_trail = self.parse_input(run_ctx)

        run_ctx.cli.writer.info("TERMINATING")
        for session_num, _ in run_ctx.cli.client.sessions.items():
            run_ctx.cli.client.logout(session_num)

        if run_ctx.cli.initiator is not None:
            run_ctx.cli.initiator.stop()
        if run_ctx.cli.interceptor is not None:
            run_ctx.cli.interceptor.stop()

        run_ctx.cli.writer.info("Complete!")
        sys.exit(0)
