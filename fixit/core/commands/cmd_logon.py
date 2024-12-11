"""
cmd_logon.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Logon` command, which facilitates logging on to a
    specific FIX session as defined in the initiator configuration file.

Usage:
    ```python
    logon_cmd = Logon()
    logon_cmd.run(cli=cli_instance, user_input="")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Logon"]

class Logon(Command):
    """
    A command to log on to a specific FIX session.

    The `Logon` command facilitates logging into a FIX session as defined in the
    initiator configuration file. It ensures the session is activated and connected
    to the FIX gateway.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Logs on to a specific session")
        self._init_arg_parser([
            {
                "name": "session_num",
                "data": {
                    "metavar": "[SESSION_NUM]",
                    "help": ARGS_SESSION_DESC,
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
        args, args_trail = self.parse_input(run_ctx, auto_session=True)

        if run_ctx.cli.initiator.isStopped():
            run_ctx.cli.initiator.start()

        run_ctx.cli.client.logon(args.session_num)
