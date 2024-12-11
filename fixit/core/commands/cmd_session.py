"""
cmd_session.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module implements the `Session` command, which provides tools for accessing
    and managing FIX session information.

    The `Session` class extends the `Command` base class and allows users to:
    - USE: Selects a session to make it active.
    - GET: Retrieves the value of a specific session property.
    - SET: Modifies the value of a specific session property.
    - LIST: Displays all active sessions.
    - VIEW (default): Displays detailed information about a specific session.

Usage:
    ```python
    session_cmd = Session()
    session_cmd.run(cli=cli_instance, user_input="get HeartBtInt")
    ```
"""

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.commands.cmd import *
from fixit.core.constants import *
from fixit.utils.common import *
from fixit.core.commands.session import *

__all__ = ["Session"]

class Session(Command):
    """
    A command to manage and interact with FIX session information.

    The `Session` command provides tools for accessing, modifying, and displaying
    session properties. It supports multiple actions such as selecting a session,
    retrieving or updating session settings, and listing active sessions.
    """

    def __init__(self, name=""):
        """ Initializes the command with its name, description, and arguments """
        super().__init__(name)
        self.set_description("Interacts with session information")
        self._init_arg_parser([
            {
                "name": "session_num",
                "data": {
                    "metavar": "[SESSION_NUM]",
                    "help": ARGS_SESSION_DESC,
                }
            },
            {
                "name": "action",
                "data": {
                    "help": ARGS_ACTION_DESC,
                    "choices": ["USE", "GET", "SET", "LIST"],
                    "type": str.upper,
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
        actions = self.parser_args["action"].choices
        args, args_trail = self.parse_input(run_ctx, actions, auto_session=True)

        if args.action is None:
            self._session_view(run_ctx, args, user_input=args_trail)
            return

        # Run action options_<action>() function
        self.run_action(run_ctx, args, user_input=args_trail, prefix="_session_")


    def _session_view(self, run_ctx, args, user_input):
        """ Displays session infromation in table format """
        config = run_ctx.cli.client.get_session_config_dict(args.session_num).items()
        table = []
        for key, value in config:
            if key == LOGGEDON:
                colour = Fore.GREEN if bool(value) else Fore.RED
                table.append([
                    run_ctx.cli.writer.colour(key, colour),
                    run_ctx.cli.writer.colour(value, colour)
                ])

            else:
                table.append([key, value])

        run_ctx.cli.writer.table(table, ["Name", "Value"],
            f"Session Settings ({args.session_num})"
        )


    def _session_use(self, run_ctx, args, user_input):
        """ Sets the curent session """
        sessions = run_ctx.cli.client.sessions
        if len(user_input) == 0:
            return

        target_session = user_input[0]
        if target_session in sessions.keys():
            run_ctx.cli.set_option("session", target_session)


    def _session_get(self, run_ctx, args, user_input):
        """ Executes the session_get sub-command """
        source_dict = run_ctx.cli.client.get_session_config_dict(args.session_num)
        Get(f"{self.name} get").run(
            user_input = user_input,
            source_dict = source_dict,
            cli = run_ctx.cli
        )


    def _session_set(self, run_ctx, args, user_input):
        """ Executes the session_set sub-command """
        Set(f"{self.name} set").run(
            user_input = user_input,
            session_num = args.session_num,
            cli = run_ctx.cli
        )
        self._session_get(run_ctx, args, user_input)


    def _session_list(self, run_ctx, args, user_input):
        """ Executes the session_list sub-command """
        source_dict = run_ctx.cli.client.sessions
        List(f"{self.name} list").run(
            user_input = user_input,
            source_dict = source_dict,
            cli = run_ctx.cli
        )
