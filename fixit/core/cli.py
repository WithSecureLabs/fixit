"""
cli.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `FixitCli` class, which serves as the command-line interface (CLI)
    application for interacting with the FIXit client and its associated tools. The CLI provides
    a comprehensive environment for managing FIX sessions, sending and manipulating messages,
    and configuring the application.

    The `FixitCli` class initializes and manages the application's runtime environment,
    handling user inputs, managing command execution, and facilitating communication with the
    base FIX client. It also supports advanced features such as message interception, session
    management, and configurable options.

Key Features:
    - Command Management: Supports dynamic loading and execution of commands.
    - Session Management: Provides tools for interacting with FIX sessions.
    - Configuration Handling: Reads and modifies configuration files and user options.
    - Preloaded Commands: Supports preloading and execution of commands on startup.
    - Interactive Environment: Offers an interactive CLI with autocompletion and contextual prompts.

Usage:
    The `FixitCli` class initializes the application's CLI environment, starts the FIX client,
    and provides an interactive loop for user interaction.
"""

import glob
import sys
import readline
import configparser
import tempfile

from os import mkdir
from os.path import exists, dirname, basename, join
from importlib import import_module
from colorama import Fore
from argparse import ArgumentTypeError

import quickfix as fix

from fixit.utils.writer import Writer
from fixit.utils import PeekableQueue
from fixit.core import FixitClient
from fixit.core import MessageStore
from fixit.core import MessageInterceptor

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.utils.parser import *
from fixit.core.constants import *

class FixitCli():
    """
    Defines the CLI application for the Fixit project.

    The `FixitCli` class initializes and manages the CLI's runtime environment,
    handles user inputs, manages commands, and facilitates communication with the
    Fixit client. It supports features like session management, message interception,
    and configuration handling.

    Attributes:
        options (dict): Application options loaded from the initiator.
        writer (Writer): Utility for printing messages to the console.
        orig_config (ConfigParser): Original configuration object.
        message_queue (PeekableQueue): Queue for passing messages to the interceptor.
        interceptor (MessageInterceptor): Intercepts and modifies FIX messages as needed.
        settings (SessionSettings): FIX session settings.
        store_factory (FileStoreFactory): Message store factory.
        log_factory (FileLogFactory): Log factory for FIX sessions.
        client (FixitClient): The base FIX client instance.
        preload_cmds (list): List of commands preloaded at startup.
        message_ctx (dict): Stores the current message context.
        message_store (MessageStore): Centralized message storage.
        parser (ArgumentParser): Argument parser for command-line inputs.
        commands (dict): Loaded commands available in the CLI.
        cmd_classes (dict): References to command classes.
        initiator (SocketInitiator): FIX session initiator.
    """

    #pylint: disable=too-many-instance-attributes
    def __init__(self, cli_args, cli_options):
        """
        Initializes the FixitCli instance.

        Args:
            cli_args (Namespace): Parsed command-line arguments.
            cli_options (dict): Application configuration options.
        """
        self._init_dirs()
        self.options = cli_options
        self._init_global_vars(cli_args)
        self.writer = Writer(cli_args.colour)
        self.orig_config, cli_args.config = self._parse_config(cli_args.config)
        self.message_queue = PeekableQueue()
        self.interceptor = MessageInterceptor(self)
        self.interceptor.start()
        self.settings = fix.SessionSettings(cli_args.config)
        self.store_factory = fix.FileStoreFactory(self.settings)
        self.log_factory = fix.FileLogFactory(self.settings)
        self.client = FixitClient(self.settings, self.writer, self.orig_config, self.message_queue, self)
        self._init_client_config(cli_args)
        self._init_preload_cmds(cli_args)
        self.message_ctx = {}
        self.message_store = MessageStore()
        self.parser = None
        self.commands = {}
        self.cmd_classes = {}
        self.initiator = None


    def _init_dirs(self):
        """ Initializes the required directory structure for the application. """
        for _dir in CONST_DIRS:
            if not exists(_dir):
                mkdir(_dir)


    def _init_preload_cmds(self, config):
        """
        Prepares a list of commands to preload and execute on startup.

        Args:
            config (Namespace): Parsed command-line arguments.
        """
        self.preload_cmds = []
        if self.options["message_store"][OPT_VAL] is not None:
            self.preload_cmds.append(f"message load {self.options['message_store'][OPT_VAL]}")

        # Check if preload argument is a file (rather than list of strings)
        if len(config.preload) == 1 and exists(config.preload[0]):
            with open(config.preload[0], "r", encoding=F_ENCODING) as preload_file:
                for line in preload_file.readlines():
                    line = line.strip()
                    if len(line) != 0 and not line.startswith("#"):
                        # append the line to the list of commands to execute
                        self.preload_cmds.append(line)

        # Else, append the string list to the list of commands to execute
        else:
            self.preload_cmds.extend(config.preload)


    def _parse_config(self, config_file):
        """
        Parses the configuration file and applies interceptor settings.

        Args:
            config_file (str): Path to the configuration file.

        Returns:
            tuple: Original and modified configuration objects.
        """
        config = configparser.ConfigParser(strict=False)
        config.read(config_file)
        config_orig = configparser.ConfigParser(strict=False)
        config_orig.read(config_file)

        try:
            if config['SESSION']['FixitInterceptHost'] is not None:
                config['SESSION']['SocketConnectHost'] = config['SESSION']['FixitInterceptHost']

            if config['SESSION']['FixitInterceptPort'] is not None:
                config['SESSION']['SocketConnectPort'] = config['SESSION']['FixitInterceptPort']
        except KeyError:
            pass

        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.ini')
        with (temp_file as modified_temp_config_file):
            config.write(modified_temp_config_file)
            modified_temp_config_path = modified_temp_config_file.name

        return config_orig, modified_temp_config_path


    def get_verbosity(self):
        """ Retrieves the verbosity level of the CLI. """
        return True if self.options["verbose"][OPT_VAL] == "True" else False


    def set_message_ctx(self, message_ctx):
        """ Sets the application's message context. """
        self.message_ctx = message_ctx


    def clear_message_ctx(self):
        """ Clears the application's message context. """
        self.message_ctx = {}


    def get_message_ctx(self, key=None, prefix=""):
        """ Retrieves the application's message context. """
        if key is None:
            return self.message_ctx
        try:
            return f"{prefix}{self.message_ctx[key]}"
        except KeyError:
            return ""


    def get_session(self):
        """ Retrieves the current session value. """
        return self.options["session"][OPT_VAL]


    def get_option(self, key):
        """ Retrieves the value of an application option. """
        return self.options[key][OPT_VAL]


    def _init_global_vars(self, cli_args):
        """
        Modifies global variables based on user arguments.

        Args:
            cli_args (Namespace): Parsed command-line arguments.
        """
        global SOH_UNI
        self.options["fix_delim"][OPT_VAL] = cli_args.fix_delim
        SOH_UNI["value"] = self.options["fix_delim"][OPT_VAL]

        global RESP_DELAY
        self.options["resp_delay"][OPT_VAL] = cli_args.resp_delay
        RESP_DELAY["value"] = float(self.options["resp_delay"][OPT_VAL])

        global FUZZ_DELAY
        self.options["fuzz_delay"][OPT_VAL] = cli_args.fuzz_delay
        FUZZ_DELAY["value"] = float(self.options["fuzz_delay"][OPT_VAL])


    def _init_client_config(self, cli_args):
        """ Initializes client configuration and credentials. """
        self.options["username"][OPT_VAL] = cli_args.username
        self.client.set_username(cli_args.username)

        self.options["password"][OPT_VAL] = cli_args.password
        self.client.set_password(cli_args.password)

        self.options["newpassword"][OPT_VAL] = cli_args.newpassword
        self.client.set_newpassword(cli_args.newpassword)

        self.options["log_heartbeat"][OPT_VAL] = cli_args.log_heartbeat
        self.client.set_log_heartbeat(cli_args.log_heartbeat)

        self.options["message_store"][OPT_VAL] = cli_args.store
        self.options["session"][OPT_VAL] = cli_args.session

        self.options["seq_seed"][OPT_VAL] = cli_args.seq_seed
        self.client.set_seq_seed(cli_args.seq_seed)

        self.options["exp_seq_seed"][OPT_VAL] = cli_args.exp_seq_seed
        self.client.set_exp_seq_seed(cli_args.exp_seq_seed)

        self.options["verbose"][OPT_VAL] = cli_args.verbose


    def _init_command_classes(self):
        """
        Dynamically imports and initializes all command classes.

        Populates the `cmd_classes` attribute with command classes found
        in the `commands` directory.
        """
        command_classes_dict = {}

        # for each python file within the commands directory
        for module_name in glob.glob(join(f"{dirname(__file__)}/commands", "*.py")):

            # Check if the file is a cmd_ class file
            module_file = basename(module_name)[:-3]
            if module_file.startswith("cmd_"):

                # Import the class from the module and store a reference to it within
                # the COMMAND_CLASSES disctionary with the class name as the key
                module_import = import_module(f"fixit.core.commands.{module_file}")

                for module_class in getattr(module_import, "__all__"):
                    command_classes_dict[f"{module_class.upper()}"] = getattr(
                        module_import, module_class
                    )
        self.cmd_classes = command_classes_dict


    def start(self):
        """
        Starts the CLI application.

        This method initializes commands, prepares the FIX client,
        and sets up the interactive environment.
        """
        self.parser = ArgumentParser(prog="", description="Do a thing", add_help=False)
        self.parser.add_argument(
            "cmd", help="Command to run", metavar="<CMD>", nargs="?"
        )

        # For each class defined in the cmd_classes, initialize and store within the commands List
        self._init_command_classes()
        for cmd_name, _ in self.cmd_classes.items():
            self.commands[cmd_name] = self.cmd_classes[cmd_name](cmd_name.lower())

        # set command autocomplete for each command
        readline.set_completer(SimpleCompleter(
            [cmd.lower() for cmd in self.commands]
        ).complete)
        readline.parse_and_bind('tab: complete')

        # Execute the banner command to display the banner on startup
        self.commands["BANNER"].run(
            user_input=[""],
            cli=self
        )

        # Print interceptor satus
        int_status = self.interceptor.get_status()
        if int_status is not None:
            self.writer.info(int_status)

        # Initialize the FIX socket initiator
        try:
            self.initiator = fix.SocketInitiator(
                self.client, self.store_factory,
                self.settings, self.log_factory
            )
        except Exception as e:
            self.writer.error(str(e))
            self.commands["EXIT"].run(
                user_input=[""],
                cli=self
            )

        # For each session found within the configuration supplied, login
        for session_num, _ in self.client.sessions.items():
            self.commands["LOGON"].run(
                user_input=[session_num],
                cli=self
            )


    def run(self):
        """
        Executes the application's main interactive loop.

        Prompts the user for input, parses commands, and executes them
        in an interactive environment.
        """
        while True:

            # Prompt for user input
            self.client.set_prompting(True)

            # Get session and msg context
            sess = f"SESS-{self.get_session().upper()}"
            msg_ctx = self.get_message_ctx('id','/')

            user_input = self.writer.prompt(f"\n[FIX/{sess}{msg_ctx}]> ",
                Fore.BLUE, self.preload_cmds
            )

            self.client.set_prompting(False)

            # If a preload CMD was run, remove it
            if len(self.preload_cmds) != 0:
                self.preload_cmds.pop(0)

            # Process user input
            args, _ = self.parser.parse_known_args_silent(user_input)
            try:
                if str(args.cmd).upper() in self.commands:
                    user_input.remove(args.cmd)
                    self.commands[args.cmd.upper()].run(
                        user_input=user_input,
                        cli=self
                    )

            except (InvalidArgsError, InvalidSessionError) as _:
                self.writer.warning("Invalid Command!")

            except NeedHelpException as _:
                pass
