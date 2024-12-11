"""
common.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines miscellaneous utility functions that are commonly used across
    various components of the Fixit application. These utilities provide support for
    tasks such as UUID generation, string manipulation, timestamp creation, and message
    processing.

Key Features:
    - UUID Generation: Create unique identifiers for messages or files.
    - String and Byte Message Handling: Convert between string, byte
      strings, and encoded representations.
    - Timestamp Creation: Generate formatted UTC timestamps.
    - FIX Message Operations: View, expand, and extract types from FIX messages.

Usage:
    The `Utils` class is designed to be used across the Fixit application for
    common tasks. Example:
        ```python
        unique_id = Utils.gen_uuid()
        timestamp = Utils.gen_timestamp()
        ```
    It also provides methods for interacting with FIX messages:
        ```python
        Utils.message_view(run_ctx, message)
        ```
"""

import quickfix as fix

#pylint: disable=wildcard-import,unused-wildcard-import
from os import path
from uuid import uuid4
from datetime import datetime
from fixit.core.constants import *

class Utils():
    """
    Implements multiple common utilities for use across the Fixit application.

    This class provides static methods for generating unique identifiers,
    handling string and byte conversions, creating timestamps, and interacting
    with FIX messages.
    """

    @staticmethod
    def gen_uuid():
        """ Returns a UUID as a string """
        return str(uuid4())


    @staticmethod
    def bytes_to_ascii(string, encode=False):
        """ Converts a byte string to an ASCII string """
        if string is None:
            string = ""

        try:
            string = string.decode("unicode_escape")

        except AttributeError:
            pass

        return string.encode(M_ENCODING) if encode else string


    @staticmethod
    def str_to_bytestr(value):
        """ Converts an ASCII string into a byte string """
        if isinstance(value, bytes):
            return value

        if isinstance(value, int):
            value = str(value)

        return bytes(value, M_ENCODING)


    @staticmethod
    def val_to_str_bytes(value):
        """ Converts an arbitrary value into its string byte representation """
        if isinstance(value, bytes):
            return value

        if isinstance(value, int):
            return bytes(str(value).encode(M_ENCODING))

        if isinstance(value, str):
            return bytes(value)

        return value


    @staticmethod
    def gen_timestamp(fmt="string", offset=0):
        """ Generate a timrstamp string """
        if fmt == "number":
            return datetime.timestamp(datetime.utcnow())

        return str((datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f"))[:-3])


    @staticmethod
    def dict_get_value(source_dict, name):
        """ attempts to return the value from a dictonary based of a given key """
        try:
            return source_dict[name]
        except KeyError:
            return INVALID


    @staticmethod
    def gen_file_name(name, fmt, stamp=True):
        """ Returns a file name """
        timestamp = f"-{Utils.gen_timestamp()}" if stamp else ""
        return f"{name}{timestamp}.{fmt.strip('.')}"


    @staticmethod
    def message_view(run_ctx, message):
        """ Prints the full message as specified by a provided history ID """
        if message is None:
            return None

        run_ctx.cli.client.msg_print(message, limit=False)
        return ""


    @staticmethod
    def message_expand(run_ctx, message, data_dict=None, filter=".*"):
        """ Describes each message field for a specific message using its history ID """
        if message is None:
            return

        run_ctx.cli.client.msg_print(message, expand=True, data_dict=data_dict, filter=filter)
        return


    @staticmethod
    def message_get_type(run_ctx, message, output=True):
        """ Prints the MsgType value for the specified message """
        if message is None:
            return None

        msg_type, msg_type_name_orig = (
            run_ctx.cli.client.get_message_type(message)
        )

        msg_type_name = run_ctx.cli.writer.colour(
            msg_type_name_orig, Fore.LIGHTCYAN_EX
        )

        if output:
            run_ctx.cli.writer.print(
                f"MsgType: {msg_type} ({msg_type_name})"
            )

        return msg_type_name_orig


    @staticmethod
    def msg_str_calc_length(message):
        """ Calculates and returns the BodyLength (9) field of a FIX message """
        msg_fields = message.split(SOH_UNI['value'])
        length = len(SOH_UNI['value'].join(msg_fields[2:-2]) + SOH_UNI['value'])
        return length


    @staticmethod
    def msg_str_calc_chksum(message):
        """ Calculates and returns the CheckSum (10) field of a FIX message """
        checksum = 0
        message = message.replace(SOH_UNI['value'], SOH_BIN)
        for c in message[:message.index(f"{SOH_BIN}10=")]:
            checksum += ord(c)
        checksum = str((checksum % 256) + 1).zfill(3)
        return checksum


    @staticmethod
    def msg_set_field(message, f_num, f_value):
        """
        Sets a specific field in a FIX message.

        Args:
            message (quickfix.Message): The message to modify.
            f_num (str): The field number to set.
            f_value (str): The value to assign to the field.

        Returns:
            quickfix.Message: The updated FIX message.
        """
        if message is None:
            return message

        if f_num in FIX_HEAD_FIELDS:
            message.getHeader().setField(fix.StringField(f_num, f_value))
        else:
            message.setField(fix.StringField(f_num, f_value))

        return message


    @staticmethod
    def msg_str_get_field(message, field_num):
        """
        Returns the value of a specific field in a string-formatted FIX message.

        Args:
            name (int): The field number to get the value of.

        Returns:
            str: The field value from the message
        """
        field_num = int(field_num)
        field_value = None

        if isinstance(message, bytes):
            message = Utils.bytes_to_ascii(message)

        SOH = SOH_UNI['value'] if message.endswith(SOH_UNI['value']) else SOH_BIN
        for _, field in enumerate(message.split(SOH)):
            if field.startswith(f"{field_num}="):
                field_value = field.solit("=", 1)[1]
                break

        if field_value is None:
            raise fix.FieldNotFound()

        return field_value


    @staticmethod
    def msg_str_set_field(message, field_num, value):
        """
        Updates the value of a specific field in a string-formatted FIX message.

        Args:
            message (str): The FIX message string.
            field_num (str): The field number to update.
            value (str | int): The new value for the field.

        Returns:
            str: The updated FIX message string.
        """
        if isinstance(value, bytes):
            value = Utils.bytes_to_ascii(value)

        SOH = SOH_UNI['value'] if message.endswith(SOH_UNI['value']) else SOH_BIN
        msg_fields = message.split(SOH)
        for i, field in enumerate(msg_fields):
            if field.startswith(f"{field_num}="):
                msg_fields[i] = (f"{field_num}={value}")
                break

        return SOH.join(msg_fields)


    @staticmethod
    def msg_str_insert_field(message, pos, field_num, value):
        """
        Updates the value of a specific field in a string-formatted FIX message.

        Args:
            message (str): The FIX message string.
            pos (int): Position in the message to insert the field
            field_num (str): The field number to update.
            value (str | int): The new value for the field.

        Returns:
            str: The updated FIX message string.
        """
        if isinstance(value, bytes):
            value = Utils.bytes_to_ascii(value)

        SOH = SOH_UNI['value'] if message.endswith(SOH_UNI['value']) else SOH_BIN
        msg_fields = message.split(SOH)
        msg_fields.insert(int(pos),f"{field_num}={value}")

        return SOH.join(msg_fields)

    @staticmethod
    def msg_str_remove_field(message, field_num):
        """
        Removes the specified field number from the message.

        Args:
            message (str): The FIX message string.
            field_num (str): The field number to remove.

        Returns:
            str: The updated FIX message string.
        """
        SOH = SOH_UNI['value'] if message.endswith(SOH_UNI['value']) else SOH_BIN
        msg_fields = message.split(SOH)
        new_msg = []
        for i, field in enumerate(msg_fields):
            if not field.startswith(f"{field_num}="):
                new_msg.append(field)

        return SOH.join(new_msg)
