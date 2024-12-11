"""
store.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `MessageStore` class, which is responsible for managing
    a centralized data store for application-wide FIX messages. The message store enables
    storage, retrieval, and modification of FIX messages across the Fixit application.

Key Features:
    - Centralized message storage for FIX messages.
    - Automatic generation and validation of unique message IDs.
    - Interactive overwrite prompts with user-defined options.
    - Supports storing FIX message metadata, including message type and string representation.

Usage:
    The `MessageStore` class is used by the Fixit application to store messages
    received or generated during FIX sessions. Messages can be added, retrieved,
    or removed using its methods. It also supports user prompts for overwriting
    existing messages when needed.
"""

#pylint: disable=wildcard-import,unused-wildcard-import
import quickfix as fix
from colorama import Fore
from fixit.core.constants import *

class MessageStore():
    """
    Manages a centralized data store for application-wide FIX messages.

    The `MessageStore` class enables storage, retrieval, and modification of
    FIX messages across the Fixit application. It provides features such as
    automatic message ID generation, metadata storage, and interactive overwrite prompts.

    Attributes:
        store (dict): Dictionary storing FIX messages and their metadata.
        auto_resp (str): User response for overwrite prompts, such as YES_ALL or NO_ALL.
    """

    def __init__(self):
        """ Initializes the MessageStore instance. """
        self.store = {}
        self.auto_resp = None


    def update_store(self, cli, message, user_input=None, store_id=None):
        """
        Appends a new message to the session's message store.

        Args:
            cli (object): The Fixit CLI instance.
            message (object): The FIX message to store.
            user_input (list, optional): User-provided input for overwrite prompts. Defaults to None.
            store_id (str, optional): A unique identifier for the message. Defaults to generating an ID.

        Returns:
            str: The store ID used for the message.
        """
        msg_type, msg_type_name = cli.client.get_message_type(message)

        if store_id is None:
            store_id = self.gen_MsgStoreID(cli, message)

        store_id = self._validate_MsgStoreID(cli, store_id, user_input=user_input)

        msg_obj = {
            "id"   : store_id,
            "type" : f"{msg_type} ({msg_type_name})",
            "msg"  : cli.client.msg_to_str(message)
        }

        cli.writer.info(f"Storing message: {msg_type_name}...")
        self.store[msg_obj["id"]] = msg_obj

        return store_id


    def remove(self, store_id):
        """ Deletes a message from the store. """
        self.store.pop(store_id)


    #pylint: disable=invalid-name
    def gen_MsgStoreID(self, cli, message):
        """Generates a new unique message store ID. """
        msg_type, msg_type_name = cli.client.get_message_type(message)
        BeginString = message.getHeader().getField(fix.BeginString().getField())
        store_id = f"{BeginString}:{msg_type_name}-{msg_type}:1"

        return store_id


    def _overwrite(self, cli, store_id, user_input=None):
        """
        Checks if a user wants to overwrite an existing message.

        Args:
            cli (object): The Fixit CLI instance.
            store_id (str): The ID of the message being checked.
            user_input (list, optional): User-provided input for overwrite prompts. Defaults to None.

        Returns:
            bool: True if the message should be overwritten, False otherwise.
        """
        if store_id in self.store and self.auto_resp not in [YES_ALL, NO_ALL]:

            # Check if a valid response is pre-provided
            if user_input is not None and len(user_input) >= 1:
                if user_input[0] in [YES_ALL, NO_ALL]:
                    self.auto_resp = user_input[0].split(" ")[0]

            warning = f"Overwite {store_id}? [YES/NO[_ALL]]: "
            warning = cli.writer.categorise(warning, cat="WARNING")
            warning = cli.writer.colour(warning, Fore.YELLOW)

            # Skip prompting if valid response is pre-provided
            if self.auto_resp == YES_ALL:
                return True
            if self.auto_resp == NO_ALL:
                return False

            response = ""
            while response not in [YES, NO, YES_ALL, NO_ALL]:
                try:
                    response = cli.writer.prompt(warning)[0].upper().strip()

                    if YES in response:
                        if ALL in response:
                            self.auto_resp = YES_ALL
                        return True

                    if NO in response:
                        if ALL in response:
                            self.auto_resp = NO_ALL
                        return False

                except IndexError:
                    pass

        return False


    #pylint: disable=invalid-name
    def _validate_MsgStoreID(self, cli, store_id, user_input=None):
        """
        Ensures the provided store ID is unique within the message store.

        Args:
            cli (object): The Fixit CLI instance.
            store_id (str): The store ID to validate.
            user_input (list, optional): User-provided input for overwrite prompts. Defaults to None.

        Returns:
            str: A unique store ID.
        """
        if self._overwrite(cli, store_id, user_input=user_input):
            return store_id

        if not store_id.split(":")[-1].isnumeric():
            store_id += ":1"

        while store_id in self.store:
            store_id = self.store[store_id]["id"].split(":")
            qualifier = int(store_id[-1]) + 1
            prefix = ':'.join(store_id[:-1])
            store_id = f"{prefix}:{qualifier}"

        return store_id
