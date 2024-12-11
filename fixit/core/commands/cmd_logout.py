"""
cmd_logout.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Logout` command, which facilitates disconnecting from an
    active FIX session.

Usage:
    ```python
    logout_cmd = Logout()
    logout_cmd.run(cli=cli_instance, user_input="")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.core.commands.cmd import *

__all__ = ["Logout"]

class Logout(Command):
    """
    A command to log out of a specific FIX session.

    The `Logout` command facilitates logging off of a FIX session as defined in the
    initiator configuration file.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name and description """
        super().__init__(name)
        self.set_description("Logs out of a specific session")
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

        run_ctx.cli.client.logout(args.session_num)
