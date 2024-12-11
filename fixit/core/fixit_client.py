"""
fix_client.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `FixitClient` class, which extends the `BaseFixApplication`
    class to implement the core functionality of the Fixit FIX client. The `FixitClient`
    manages FIX sessions, processes and generates FIX messages, and provides advanced
    capabilities for FIX protocol communication.

Key Features:
    - Message Handling:
        - Generates, modifies, and sends various FIX messages.
        - Supports raw message transmission with field-level updates.
        - Converts between FIX message formats (e.g., raw string, XML, FIX objects).
    - Advanced Utilities:
        - Expands and inspects FIX message fields.
        - Handles message specifications dynamically based on session configurations.
        - Calculates message checksums and lengths.
    - Logging and Feedback:
        - Provides detailed feedback for sent and received messages.
        - Supports configurable logging of heartbeats and other message types.

Usage:
    The `FixitClient` class is instantiated within the Fixit application to manage FIX
    sessions and interact with FIX gateways. Example:
        ```python
        client = FixitClient(session_settings, writer, config, message_queue, cli)
        client.send_message(session_num, message)
        ```
    It also supports custom message creation:
        ```python
        test_message = client.create_message(session_num, "TEST", user_input)
        client.send_message(session_num, test_message)
        ```
"""

import string
import time
import re
import glob
import itertools
import xml.etree.ElementTree as ET

from os.path import basename, join
from datetime import datetime, timedelta
from collections import OrderedDict
from colorama import Fore

import quickfix as fix

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.utils.exceptions import *
from fixit.utils.common import *

from fixit.fix import MessageCreator
from fixit.fix import BaseFixApplication

class FixitClient(BaseFixApplication):
    """
    Extends the `BaseFixApplication` to provide the main functionality for the Fixit FIX client.

    The `FixitClient` class manages FIX sessions, processes messages, and supports advanced
    features for interacting with FIX gateways. It builds upon the foundational capabilities
    of `BaseFixApplication`, adding tools for message creation, modification, and transmission.

    Attributes:
        msg_field_dict (dict): A dictionary of message fields, keyed by FIX version number
        msg_type_dict (dict): A dictionary of message types, keyed by FIX version number
        msg_data_dict (dict): The FIX data dictionaries, keyed by FIX version number
        prompting (bool): Used to know if the application is currently prompting for input or not
        log_heartbeat (bool): Controls wether heartbeat messages are logged or not
    """
    msg_field_dict = {}
    msg_type_dict = {}
    msg_data_dict = {}
    prompting = False
    log_heartbeat = False

    def __init__(self, session_settings_obj, writer, orig_config, message_queue, cli):
        """
        Initializes the `FixitClient` instance with session settings, configuration, and dependencies.

        Args:
            session_settings_obj (quickfix.SessionSettings): The session settings for the FIX connection.
            writer (Writer): The writer instance for logging and console output.
            orig_config (dict): Original configuration settings for the client.
            message_queue (PeekableQueue): Queue for storing and processing messages.
            cli (FixitCli): The CLI instance managing the application.
        """
        super().__init__()
        self.session_settings_obj = session_settings_obj
        self.writer = writer
        self.orig_config = orig_config
        self.message_queue = message_queue
        self.cli = cli
        self._gen_data_dicts()


    def create_message(self, session_num, msg_type, user_input):
        """
        Generates a FIX message template based on a specified message type.

        Args:
            session_num (str): The session number associated with the message.
            msg_type (str): The type of message to generate (e.g., "ORD-BUY", "TEST").
            user_input (list): Additional input required for specific message types.

        Returns:
            quickfix.Message: The generated FIX message, or None if the msg_type type is invalid.
        """
        sessionID = self._get_sessionID(session_num)
        symbol = "EUR/USD"

        if msg_type == "FREE":
            return MessageCreator.gen_new_message(self, sessionID=sessionID)

        if msg_type == "TEST":
            return MessageCreator.TestRequest(self, sessionID=sessionID)

        if msg_type == "ORD-BUY":
            return MessageCreator.NewOrderSingle(self, sessionID, symbol, 1, 10, fix.Side_BUY)

        if msg_type == "ORD-SELL":
            return MessageCreator.NewOrderSingle(self, sessionID, symbol, 1, 10, fix.Side_SELL)

        if msg_type == "ORD-CANCEL":
            orderHID = 1 # The history ID of an order to base the message off
            try:
                if len(user_input) > 0:
                    orderHID = int(user_input[0])

                if len(self.get_session_message_log(session_num)) >= orderHID:
                    return MessageCreator.OrderCancelRequest(self, sessionID, orderHID)
                else:
                    raise InvalidArgsError()

            except (ValueError, TypeError, InvalidArgsError, IndexError):
                self.writer.warning("Invalid History ID: new ORD-CANCEL <HISTORY ID OF ORDER>")
                return

        if msg_type == "ORD-STAT":
            orderHID = 1 # The history ID of an order to base the message off
            try:
                if len(user_input) > 0:
                    orderHID = int(user_input[0])

                if len(self.get_session_message_log(session_num)) >= orderHID:
                    return MessageCreator.OrderStatusRequest(self, sessionID, orderHID)
                else:
                    raise InvalidArgsError()

            except (ValueError, TypeError, InvalidArgsError, IndexError):
                self.writer.warning("Invalid History ID: new ORD-STAT <HISTORY ID OF ORDER>")
                return

        if msg_type == "MD-SUB":
            sub_type = fix.SubscriptionRequestType_SNAPSHOT_PLUS_UPDATES
            update_type = 0
            return MessageCreator.MarketDataRequest(
                self, sessionID, sub_type, 2, update_type, symbol
            )

        if msg_type == "MD-SUB-CANCEL":
            sub_type = fix.SubscriptionRequestType_DISABLE_PREVIOUS_SNAPSHOT_PLUS_UPDATE_REQUEST
            update_type = 0
            return MessageCreator.MarketDataRequest(
                self, sessionID, sub_type, 2, update_type, symbol
            )

        return None


    def send_test_message(self, session_num):
        """
        Sends a predefined test message to the FIX gateway.

        Args:
            session_num (str): The session number for the test message.
        """
        self.writer.info("Sending test message...")
        sessionID = self._get_sessionID(session_num)
        msg = MessageCreator.TestRequest(self, sessionID)

        fix.Session.sendToTarget(msg, sessionID)
        time.sleep(RESP_DELAY['value'])


    def send_message(self, session_num, message):
        """
        Sends an arbitrary FIX message to the gateway.

        Args:
            session_num (str): The session number associated with the message.
            message (str | quickfix.Message): The FIX message to send.
        """
        self.writer.info("Sending message...")
        sessionID = self._get_sessionID(session_num)

        if isinstance(message, str):
            message = self.str_to_msg(message)

        try:
            fix.Session.sendToTarget(message, sessionID)
            time.sleep(RESP_DELAY['value'])
        except ValueError as e:
            self.writer.error("Failed to send message!?")


    def send_raw_data(self, session_num, data, run_ctx=None, clean_up=True):
        """
        Sends raw data to the gateway, updating sequence numbers and checksums.

        Args:
            session_num (str): The session number for the raw data.
            data (str): The raw FIX data string.
            run_ctx (object, optional): Context object for managing the runtime environment.
            clean_up (bool): Wether critical feields should be automatically updated.
        """
        sessionID = self._get_sessionID(session_num)
        nextSeqNum = self.get_next_seq_num(session_num)

        if clean_up:
            data = Utils.msg_str_set_field(
                Utils.bytes_to_ascii(data), "34", int(nextSeqNum)
            )
            data = Utils.msg_str_set_field(
                data,  "9", Utils.msg_str_calc_length(data)
            )
            data = Utils.msg_str_set_field(
                data, "10", Utils.msg_str_calc_chksum(data)
            )

        # Queue and flag the message (so the interceptor can ensure it's sent)
        run_ctx.cli.message_queue.put(
            self.msg_to_str(data, binary=True).encode('ascii')
        )
        self.set_editedMessageFlag(session_num, True)
        self.set_editedMessage(session_num, data)

        self.send_message(session_num, data)


    def set_prompting(self, value):
        """ Sets the prompting state of the CLI. """
        self.prompting = value


    def set_log_heartbeat(self, value):
        """
        Toggles logging of FIX heartbeat messages.

        Args:
            value (bool): Whether to log heartbeat messages (True) or not (False).
        """
        if value is False:
            if fix.MsgType_Heartbeat not in self.ignored_messages:
                self.ignored_messages.append(fix.MsgType_Heartbeat)

        elif value is True:
            if fix.MsgType_Heartbeat in self.ignored_messages:
                self.ignored_messages.remove(fix.MsgType_Heartbeat)

        self.log_heartbeat = value


    def msg_print(self, message, prefix="", expand=False, limit=True, encode=True, data_dict=None, filter=".*"):
        """
        Prints a FIX message to the console with optional expansion of its fields.

        Args:
            message (quickfix.Message | str): The FIX message to print.
            prefix (str, optional): A prefix to add before the message.
            expand (bool, optional): Whether to expand message fields.
            limit (bool, optional): Whether to truncate the output.
            encode (bool, optional): Whether to encode the message for display.
            data_dict (dict, optional): A dictionary for field names and values.
        """
        if message is None:
            return

        if self.prompting:
            self.writer.print("")
            self.set_prompting(False)

        if expand:
            if isinstance(message, fix.Message):
                message = message.toString()

            self.msg_expand(message, output=True, encode=encode, data_dict=data_dict, filter=filter)
        else:
            self.writer.print(
                f"{prefix}{Utils.bytes_to_ascii(self.msg_to_str(message), encode)}", limit=limit
            )


    def msg_to_str(self, message, binary=False):
        """
        Converts a FIX message object to a raw string.

        Args:
            message (quickfix.Message | str): The FIX message to convert.
            binary (bool, optional): Whether to return a binary-formatted string.

        Returns:
            str: The raw FIX message string.
        """
        if isinstance(message, fix.Message):
            message = message.toString()

        if binary:
            return message.replace(SOH_UNI['value'], SOH_BIN)

        return str(self.msg_encode_binary_chars(message.replace(SOH_BIN, SOH_UNI['value'])))


    def msg_encode_binary_chars(self, message):
        result = []
        for char in message:
            if char in string.printable or char in string.whitespace:
                result.append(char)
            elif char in [SOH_BIN, SOH_UNI["value"]]:
                result.append(char)
            else:
                result.append(f"\\0x{ord(char):02x}")
        return ''.join(result)


    def str_to_msg(self, msg_str, self_repair=True, spec_str=None):
        """
        Converts a raw FIX message string to a FIX message object.

        Args:
            msg_str (str): The FIX message string.
            self_repair (bool, optional): Whether to attempt self-repair for invalid messages.
            spec_str (str, optional): Message specification string.

        Returns:
            quickfix.Message | None: The FIX message object, or None if conversion fails.
        """
        if msg_str.endswith(SOH_UNI['value']):
            msg_str = str(msg_str.replace(SOH_UNI['value'], SOH_BIN))

        try:
            if spec_str is None:
                _, spec_dict = self._get_message_spec_dict(msg_str)
            else:
                spec_dict = self.msg_data_dict[spec_str]

            message = fix.Message(msg_str, spec_dict, True)
            return message

        except InvalidMsgSpecError:
            return None

        # If InvalidMessage is thrown, attempt to repair
        except (fix.InvalidMessage) as e:
            error_message = str(e)
            if self_repair and "Expected BodyLength" in error_message:
                value = error_message.split("=",1)[1].split(",")[0]
                return self.str_to_msg(
                    Utils.msg_str_set_field(
                        msg_str.replace(SOH_BIN, SOH_UNI['value']), "9", value)
                )

            if self_repair and "Expected CheckSum" in error_message:
                value = error_message.split("=",1)[1].split(",")[0]
                return self.str_to_msg(
                    Utils.msg_str_set_field(
                        msg_str.replace(SOH_BIN, SOH_UNI['value']), "10", value)
                )

            # If not within self-repair parameters, show error
            self.writer.error(
                f"({ERR_MSG_MR01}) {error_message}\n{Utils.bytes_to_ascii(msg_str, True)}"
            )

        except KeyError:
            self.writer.error(
                f"\n({ERR_MSG_MR00}) {ERR_MSG}: {Utils.bytes_to_ascii(msg_str, True)}"
            )

        return None


    def msg_to_xml(self, message):
        """
        Converts a FIX message object to an XML string.

        Args:
            message (quickfix.Message | str): The FIX message to convert.

        Returns:
            str: The XML-formatted message string.
        """
        if isinstance(message, str):
            message = self.str_to_msg(message)

        return message.toXML()


    def get_message_type(self, message):
        """
        Identifies the message type of a FIX message.

        Args:
            message (quickfix.Message | str): The FIX message to inspect.

        Returns:
            tuple: A tuple containing the message type and its name.
        """
        if isinstance(message, str):
            message = self.str_to_msg(message)
            if message is None:
                return (UNKNOWN, UNKNOWN)

        try:
            spec, _ = self._get_message_spec_dict(message)
            msg_type = message.getHeader().getField(fix.MsgType().getField())
            msg_type_name = self.msg_type_dict[spec][msg_type]

        except(KeyError, InvalidMsgSpecError):
            msg_type_name = UNKNOWN

        return (msg_type, msg_type_name)


    def _get_message_spec_dict(self, message):
        """
        Retrieves the message specification dictionary based on the message type.

        Args:
            message (quickfix.Message | str): The FIX message to inspect.

        Returns:
            tuple: A tuple containing the specification string and dictionary.
        """
        if not isinstance(message, str):
            message = self.msg_to_str(message)

        msg_type = UNKNOWN
        message = message.replace("\n", "")
        for field in message.replace(SOH_BIN, SOH_UNI['value']).split(SOH_UNI['value']):
            if field.startswith("35="):
                msg_type = field.split("=")[1]
                break

        for spec_str in ["FIXT11", "FIX50", "FIX44", "FIX43", "FIX42", "FIX41", "FIX40"]:
            data_dictionary = fix.DataDictionary(self.msg_data_dict[spec_str])
            if data_dictionary.isMsgType(msg_type):
                return spec_str, self.msg_data_dict[spec_str]

        # If the message type is not found in any of the above specs,
        # determine based on the BeginString field as a backup
        return self._get_message_spec_dict_from_bs(message)


    def _get_message_spec_dict_from_bs(self, message):
        """
        Retrieves the message specification dictionary based on the BeginString field.

        Args:
            message (quickfix.Message | str): The FIX message to inspect.

        Returns:
            tuple: A tuple containing the specification string and dictionary.
        """
        spec = ""
        if isinstance(message, str):
            message = message.replace("\n", "")
            if SOH_UNI['value'] in message:
                message = str(message.replace(SOH_UNI['value'], SOH_BIN))

            spec = message.split(SOH_BIN)[0][2:]

        else:
            spec = message.getHeader().getField(fix.BeginString().getField())

        # With the spec string extracted, attempt to retrieve the spec dict
        try:
            spec_str = spec.replace(".", "")
            return spec_str, self.msg_data_dict[spec_str]

        except (KeyError) as e:
            spec_str = str(e).replace("'", "")
            self.writer.error(
                f"{ERR_MSG}: Unknown message spec: {spec} ({SPEC_DIR}{spec_str}.xml)"
            )
            raise InvalidMsgSpecError from e


    def _gen_data_dicts(self):
        """ Generates dictionaries for FIX message fields and types based on FIX specifications."""

        # Create a list of FIX spec files
        specs = []
        for spec_file in glob.glob(join(SPEC_DIR, "*.xml")):

            if basename(spec_file).startswith("FIX"):
                specs.append(spec_file)

        # For each spec fiels, build an associated filed and type dict
        for spec in specs:

            # Initialize dictionary objects
            field_dict = {}
            type_dict = {}

            # Read the content of the session's FIX specification file
            with open(spec, "rb") as f:

                # Retrieve all fields from the specification
                xml = f.read()
                fields = ET.fromstring(xml).find("fields")

                # For each field, append to the dictionary
                for field in fields.iter("field"):
                    # Append field with number as key
                    field_dict[field.attrib["number"]] = {
                        "name": field.attrib["name"],
                        "type": field.attrib["type"]
                    }

                    # Append field with name as key
                    field_dict[field.attrib["name"]] = {
                        "number": field.attrib["number"],
                        "type": field.attrib["type"]
                    }

                    # Check if the name if the field is of MsgType
                    if field.attrib["name"] == "MsgType":
                        # For each message type append to message type dictonary
                        for mtype in field:
                            type_num = mtype.attrib["enum"]
                            type_name = mtype.attrib["description"]
                            type_dict[type_num] = type_name

            # Set the session dictionaries to these generated ones
            self.msg_data_dict[basename(spec)[:-4]] = fix.DataDictionary(spec)
            self.msg_field_dict[basename(spec)[:-4]] = field_dict
            self.msg_type_dict[basename(spec)[:-4]] = type_dict


    def msg_expand(self, message, output=False, encode=False, data_dict=None, filter=".*"):
        """
        Print and return the details of each field within a FIX message.

        Args:
            message (quickfix.Message | str): The FIX message to expand.
            output (bool, optional): Whether to print the expanded details.
            encode (bool, optional): Whether to encode the field values.
            data_dict (dict, optional): A dictionary for field names and values.

        Returns:
            list: A list of dictionaries containing field details.
        """
        msg_details = self._msg_expand(message, data_dict=data_dict) # new
        if output:
            for row in msg_details:
                if (
                    re.search(fr".*{filter}.*", row['field_name'], re.IGNORECASE) or
                    re.search(fr".*{filter}.*", row['field_val'], re.IGNORECASE)
                ):
                    name_str = self.writer.colour(row['field_name'], Fore.LIGHTCYAN_EX)
                    field_val = str(Utils.bytes_to_ascii(row['field_val'], encode))[2:-1]
                    self.writer.print(
                        f"{row['field_num']}({name_str})={field_val}"
                    )

        return msg_details


    def msg_to_list(self, message):
        """ Returns the message as a List of field_number, vield_value pairs"""
        if isinstance(message, fix.Message):
            message = self.msg_to_str(message)

        SOH = SOH_UNI['value'] if message.endswith(SOH_UNI['value']) else SOH_BIN
        fields_list = []
        msg_fields = message.split(SOH)
        for i, field in enumerate(msg_fields):
            fields_list.append(field.split("=", 1))

        return fields_list


    def _msg_expand(self, message, data_dict=None):
        """
        Expands a FIX message into a list of field properties.

        Args:
            message (fix.Message | str): The FIX message to expand.
            data_dict (dict, optional): A field specification dictionary

        Returns:
            list: A list of dictionaries representing each field in the message - containing:
                - `field_num` (str): The field number.
                - `field_name` (str): The field name.
                - `field_val` (str): The field value.
        """
        msg_details, parsed = [], OrderedDict()
        msg_orig = message

        if isinstance(message, fix.Message):
            message = self.msg_to_str(message)

        if message is None:
            return msg_details

        try:
            spec_field_dict = self._get_message_spec_dict(message)[0] if data_dict is None else data_dict
            message_fields = self.msg_to_list(message)
            msg_details = self._get_field_details(message_fields, spec_field_dict)

        except InvalidMsgSpecError:
            msg_details = []

        return msg_details


    def _get_field_details(self, message_fields, spec):
        """
        Parses an XML file and extracts details for each <field> tag.

        Args:
            message_fields (List): A list of message field number and value pairs
            spec (dict): A dictionary containing all FIX spec fields

        Returns:
            list: A list of dictionaries containing field details.
        """
        msg_details = []

        for field in message_fields:
            if len(field) <= 1:
                continue

            field_num, field_val = field

            field_type = None
            try:
                field_type = self.msg_field_dict[spec][field_num]["type"]
            except KeyError:
                field_name = UNKNOWN

            field_name = None
            try:
                field_name = self.msg_field_dict[spec][field_num]["name"]
            except KeyError:
                field_name = UNKNOWN

            # Append message line
            msg_details.append({
                "field_num": field_num,
                "field_name": field_name,
                "field_val": field_val
            })

        return msg_details
