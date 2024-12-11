"""
base_application.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `BaseFixApplication` class, which serves as the foundational FIX
    application for the Fixit framework. It extends the QuickFIX `Application` class, implementing
    core functionalities required to interact with FIX sessions. This includes session management,
    message logging, and handling of administrative and application-level messages.

Key Features:
    - Session Management:
        - Initialization of session-specific variables and settings.
        - Handling logon, logout, and session status monitoring.
    - Message Processing:
        - Administrative and application-level message handling.
        - Logging of sent and received FIX messages.
    - ID Generation:
        - Generates unique IDs for orders, executions, quotes, and test requests.
    - Message Logging:
        - Logs FIX messages to memory and files, with support for intercepted messages.
    - Sequence Number Management:
        - Ensures correct sequence numbers for message synchronization.

Usage:
    The `BaseFixApplication` class is intended to be extended within the Fixit application
    It manages interactions with FIX sessions, processes incoming and outgoing messages,
    and logs communication details for debugging and analysis.
"""

import csv
import re
import time
import queue

from datetime import datetime
from colorama import Fore

import quickfix as fix

#pylint: disable=wildcard-import,unused-wildcard-import
from fixit.core.constants import *
from fixit.utils.exceptions import *
from fixit.utils.common import *

class BaseFixApplication(fix.Application):
    """
    Implements a base FIX class for managing FIX protocol sessions and messages.

    The `BaseFixApplication` class provides core functionality for interacting with FIX gateways,
    including session management, message handling, logging, and configuration. It acts as a
    foundational class for building the borader Fixit application.

    Attributes:
        ID variables (int): session-wide veriables for storing the lastes ID generated for that session
        session* (dict): A set of dictionaries that hold session-specific information, keyed by session ID.
        NextExpSeqNum (int): Used to hold the value of the next expected message sequence number, if required
        NextSenderSeqNum (int): Used to hold the value of the next expected sender sequence number, if required
        username (str): Holds the username value for the current session
        password (str): Holds the password value for the current session
        newpassword (str): Holds the new password value, used to perform password updates
        config_recon_int (int): The interval in seconds to wait when attempting a LOGON
        message_queue (PeekableQueue): a reference to the interceptors message queue
        ignored_messages (List): A list of messages to ignore when logging actigvity to the screen
    """

    # ID variables
    orderID         = 0
    ClOID           = 0
    execID          = 0
    MDReqID         = 0
    TestReqID       = 0
    OrdStatusReqID  = 0
    QuoteReqID      = 0

    # Session variables
    session_settings_obj            = None
    sessions                        = {}
    session_settings                = {}
    session_config_dict             = {}
    session_message_log             = {}
    session_message_count           = {}
    session_message_log_file        = {}
    session_message_store           = {}
    session_attempting_logon        = {}
    session_logon_attempts          = {}
    session_BeginString             = {}
    session_NextExpSeqNum           = {}
    session_NextSenderSeqNum        = {}
    session_loggedon                = {}
    session_seqNum                  = {}
    session_editedMessageFlag       = {}
    session_editedMessage           = {}

    NextExpSeqNum = None
    NextSenderSeqNum = None

    # Variables used for session credentials
    username = ""
    password = ""
    newpassword = ""

    config_recon_int = 30 # overriden by config onCreate
    message_queue = None

    # Used to filter logging feedback to the terminal
    ignored_messages = [
        fix.MsgType_Heartbeat,
    ]

    def onCreate(self, sessionID):
        """
        Called when a new FIX session is created.
        This method initializes session-specific variables, logs the session creation,
        and invokes a logout to prevent automatic logon during session initialization.

        Args:
            sessionID (quickfix.SessionID): The ID of the created session.
        """
        self._initialize_session(sessionID)
        self.writer.info(
            f"\nFIX Session created: {sessionID.toString()}."
        )
        fix.Session.lookupSession(sessionID).logout()


    def _initialize_session(self, sessionID):
        """ Initializes all session-specific cariables required by a discrete FIX session """

        # Store the session information within the sessions dictionary
        session_num = str(len(self.sessions.keys()))
        self.sessions[session_num] = {
            "id": session_num,
            "sessionID": sessionID
        }

        # Convert session-settings object into a dictionary of values
        self.session_settings[sessionID.toString()] = self.session_settings_obj.get(sessionID)

        # Initialize local valies from the session configuration
        self.session_BeginString[sessionID.toString()] = (
            self.session_settings[sessionID.toString()].getString(CONFIG_KEYS["BEGINSTRING"])
        )

        # Store the config reconnect_interval value
        self.config_recon_int = self.session_settings[sessionID.toString()].getInt(
            CONFIG_KEYS["RECONNECT_INTERVAL"]
        )

        # Initialize message logging infomration
        self._gen_log_file(session_num)
        #self._gen_log_file(session_num)
        self.session_attempting_logon[sessionID.toString()] = False
        self.session_message_log[sessionID.toString()] = []
        self.session_message_count[sessionID.toString()] = -1

        # Initialize message store infomration
        self.session_message_store[sessionID.toString()] = {}

        # Initialize next expected seq num
        self.session_NextExpSeqNum[sessionID.toString()] = self.NextExpSeqNum
        self.session_NextSenderSeqNum[sessionID.toString()] = self.NextSenderSeqNum
        self.session_seqNum[sessionID.toString()] = self.NextSenderSeqNum
        self.session_loggedon[sessionID.toString()] = False
        self.session_logon_attempts[sessionID.toString()] = 0

        # Initialize Message editing information
        self.session_editedMessageFlag[sessionID.toString()] = False
        self.session_editedMessage[sessionID.toString()] = None

        # Update session details Host and Port to match server
        # (Interceptor should be transparent)
        self.set_session_config(
            CONFIG_KEYS["SOCKET_CONNECT_HOST"],
            self.orig_config.get("SESSION", CONFIG_KEYS["SOCKET_CONNECT_HOST"]),
            session_num
        )
        self.set_session_config(
            CONFIG_KEYS["SOCKET_CONNECT_PORT"],
            self.orig_config.get("SESSION", CONFIG_KEYS["SOCKET_CONNECT_PORT"]),
            session_num
        )


    def onLogon(self, sessionID): #pylint: disable=arguments-renamed
        """
        Called when a logon is successful.
        Marks the session as logged on and resets the session logon attempts.

        Args:
            sessionID (quickfix.SessionID): The ID of the session that successfully logged on.
        """
        self.writer.info(
            f"\nSuccessful Logon to session '{sessionID.toString()}'."
        )
        self.session_loggedon[sessionID.toString()] = True
        self.session_logon_attempts[sessionID.toString()] = 0


    def logon(self, session_num):
        """
        Initiates a logon process for the specified session.

        Args:
            session_num (str): The session number to log on.
        """
        sessionID = self._get_sessionID(session_num)
        wcreds = " with credentials" if (self.username != "" or self.password != "") else ""

        if self.isLoggedOn(session_num):
            return

        self.writer.info(
            f"\nLogging on to '{sessionID.toString()}'{wcreds}...\n"
        )
        fix.Session.lookupSession(sessionID).logon()

        # Track when the time when logon was first attempted
        starttime = time.perf_counter()
        self.session_attempting_logon[sessionID.toString()] = True

        # Construct an appropriate timeout based on the RECONNECT_INTERVAL and LOGON_TIMEOUT
        interval = self.get_session_config(CONFIG_KEYS["RECONNECT_INTERVAL"], session_num)
        timeout = self.get_session_config(CONFIG_KEYS["LOGON_TIMEOUT"], session_num)

        threshhold = int(
            (int(interval) if interval != INVALID else DEFAULT_RECONNECT_INTERVAL) +
            (int(timeout) if timeout != INVALID else DEFAULT_LOGON_TIMEOUT)
        )

        # Continue to poll if the session has logged on or not
        while self.isLoggedOn(session_num) is False:
            if time.perf_counter() - starttime > threshhold:
                self.writer.error(
                    f"\nLogon failed for session '{sessionID.toString()}'{wcreds}."
                )
                # Force a logout to kill engine auth loop
                fix.Session.lookupSession(sessionID).logout()
                break

            time.sleep(POLL_TIME)
            continue

        # Revert reconnect interval to original value
        self.set_session_config(
            CONFIG_KEYS["RECONNECT_INTERVAL"], self.config_recon_int, session_num
        )

        self.session_attempting_logon[sessionID.toString()] = False

        return

    def onLogout(self, sessionID): #pylint: disable=arguments-renamed
        """
        Called when a logout is successful.
        Marks the session as logged out and logs the event.

        Args:
            sessionID (quickfix.SessionID): The ID of the session that logged out.
        """
        if not self.session_attempting_logon[sessionID.toString()]:
            self.writer.info(
                f"\nLogged out of session '{sessionID.toString()} complete'."
            )
            self.session_loggedon[sessionID.toString()] = False


    def logout(self, session_num):
        """
        Logs out of the specified session.

        Args:
            session_num (str): The session number to log out.
        """
        sessionID = self._get_sessionID(session_num)

        # Temporarily reduce reconnect interval
        self.set_session_config(
            CONFIG_KEYS["RECONNECT_INTERVAL"], MANUAL_RECON_INT,
            self._get_session_num(sessionID)
        )

        # If the application is already trying to log out, return
        if self.session_attempting_logon[sessionID.toString()]:
            return

        self.writer.info(
            f"\nLogging out of '{sessionID.toString()}'...\n"
        )
        fix.Session.lookupSession(sessionID).logout()

        # Build a timeout threshhold based on configuration values
        timeout = self.get_session_config(CONFIG_KEYS["LOGOUT_TIMEOUT"], session_num)
        threshhold = int(timeout) if timeout != INVALID else DEFAULT_LOGOUT_TIMEOUT

        # Attempt to confirm logout for threshhold timeframe
        starttime = time.perf_counter()
        while self.isLoggedOn(session_num) is True:
            if time.perf_counter() - starttime > threshhold:
                self.writer.error(
                    f"\nLogout failed for session '{sessionID.toString()}'."
                )
                break

            time.sleep(POLL_TIME)
            continue

        return


    def isLoggedOn(self, session_num):
        """ Returns true if a specified session type is logged on """
        sessionID = self._get_sessionID(session_num)
        return fix.Session.lookupSession(sessionID).isLoggedOn()


    def toApp(self, message, sessionID):
        """
        Called when an application message is sent out of the initiator.
        Logs the outgoing application-level message.

        Args:
            message (quickfix.Message): The FIX message being sent.
            sessionID (quickfix.SessionID): The session ID associated with the message.
        """
        self._log_message(APP_O, message, sessionID)

    def fromApp(self, message, sessionID):
        """
        Called when an application message is received by the initiator.
        Logs the incoming application-level message.

        Args:
            message (quickfix.Message): The FIX message being received.
            sessionID (quickfix.SessionID): The session ID associated with the message.
        """
        self._log_message(APP_I, message, sessionID)

    def toAdmin(self, message, sessionID):
        """
        Called when an administrative message is sent out of the initiator.
        Handles authentication details, corrects sequence numbers, and logs the message.

        Args:
            message (quickfix.Message): The FIX admin message being sent.
            sessionID (quickfix.SessionID): The session ID associated with the message.
        """
        if fix.Session.lookupSession(sessionID) is None:
            return

        msg_type, _ = self.get_message_type(message)
        if msg_type == fix.MsgType_Logon:
            self.session_attempting_logon[sessionID.toString()] = True
            self.session_logon_attempts[sessionID.toString()] += 1

            if self.session_logon_attempts[sessionID.toString()] >= 5:
                self.writer.error(
                    f"\nConnection lost session '{sessionID.toString()}'."
                )
                fix.Session.lookupSession(sessionID).logout()
                return

            # if username and password found, insert into the logon message
            if self.username not in ["", None]:
                message.setField(fix.Username(self.username))
            if self.password not in ["", None]:
                message.setField(fix.Password(self.password))
            if self.newpassword not in ["", None]:
                message.setField(fix.NewPassword(self.newpassword))

            # Correct Sequence Number if required
            if self.session_NextSenderSeqNum[sessionID.toString()]:
                s = fix.Session.lookupSession(sessionID)
                s.setNextSenderMsgSeqNum(int(
                    self.session_NextSenderSeqNum[sessionID.toString()]
                ))
                message.getHeader().setField(fix.MsgSeqNum(int(
                    self.session_NextSenderSeqNum[sessionID.toString()]
                )))
                self.session_NextSenderSeqNum[sessionID.toString()] = None

            # Correct next expected seq number if required
            if self.session_NextExpSeqNum[sessionID.toString()]:

                message.setField(fix.NextExpectedMsgSeqNum(int(
                    self.session_NextExpSeqNum[sessionID.toString()]
                )))

                # If the session is logged on, clear this field - only needed once
                if self.session_loggedon[sessionID.toString()]:
                    self.session_NextExpSeqNum[sessionID.toString()] = None
                    message.removeField(fix.NextExpectedMsgSeqNum().getField())

            # Set DefaultApplExtID if present in config
            try:
                DefaultApplExtID = self.session_settings[sessionID.toString()].getString('DefaultApplExtID')
                message.setField(fix.DefaultApplExtID(int(DefaultApplExtID)))
            except fix.ConfigError:
                pass

            # Set TargetSubID if present in config
            try:
                TargetSubID = self.session_settings[sessionID.toString()].getString('TargetSubID')
                message.getHeader().setField(fix.TargetSubID(TargetSubID))
            except fix.ConfigError:
                pass

            # Set SenderLocationID if present in config
            try:
                SenderLocationID = self.session_settings[sessionID.toString()].getString('SenderLocationID')
                message.getHeader().setField(fix.SenderLocationID(SenderLocationID))
            except fix.ConfigError:
                pass

        self._log_message(ADM_O, message, sessionID)

        # Check if LOGOUT or LOGON is being sent
        if msg_type == fix.MsgType_Logout and self.cli.get_verbosity():
            self.writer.warning("LOGOUT sent to server!")
        if msg_type == fix.MsgType_Logon and self.cli.get_verbosity():
            self.writer.warning("LOGON sent to server!")


    def fromAdmin(self, message, sessionID):
        """
        Called when an administrative message is received by the initiator.
        Logs the incoming admin-level message and handles special cases such as logouts.

        Args:
            message (quickfix.Message): The FIX admin message being received.
            sessionID (quickfix.SessionID): The session ID associated with the message.
        """
        self._log_message(ADM_I, message, sessionID)
        msg_type, _ = self.get_message_type(message)

        # Check if LOGON or LOGOUT is being recieved
        if msg_type == fix.MsgType_Logout and self.cli.get_verbosity():
            self.writer.warning("LOGOUT recieved from server!")
        if msg_type == fix.MsgType_Logon and self.cli.get_verbosity():
            self.writer.warning("LOGON recieved from server!")

        # Check if the message has a text field (as it may have information)
        try:
            text = message.getField(fix.Text().getField())
            self.writer.warning(f"Msg Text (58): {text}")

            r_MsgseqNum = r"^.*(MsgSeqNum).*expecting ([0-9]+).*$"
            r_NextExpectedMsgSeqNum = r"^.*(NextExpectedMsgSeqNum).*expecting ([0-9]+).*$"

            # Check if the text is informing us that the SeqNum is wrong
            result = re.search(r_MsgseqNum, text)
            if result is not None:
                try:
                    self.session_NextSenderSeqNum[sessionID.toString()] = int(result.group(2)) + 2
                    self.writer.info(f"Msg Seq set to {result.group(2)}")
                except IndexError:
                    pass

            # Check if the text is informing us that the NextExpSeqNum is wrong
            result = re.search(r_NextExpectedMsgSeqNum, text)
            if result is not None:
                try:
                    self.session_NextExpSeqNum[sessionID.toString()] = int(result.group(2)) + 2
                    self.writer.info(f"Next Exp Seq set to {result.group(2)}")
                except IndexError:
                    pass

        except fix.FieldNotFound:
            pass


    def _log_message(self, msg_route, message, sessionID):
        """
        Logs a message to memory, updates session message logs, and handles message interception.

        Args:
            msg_route (str): The message route (e.g., APP_I, ADM_O).
            message (quickfix.Message): The FIX message being logged.
            sessionID (quickfix.SessionID): The session ID associated with the message.
        """
        if sessionID.toString() not in self.session_message_count:
            self._initialize_session(sessionID)

        session_num = self._get_session_num(sessionID)
        msg_type, msg_type_name = self.get_message_type(message)
        msg_type_name_c = self.writer.colour(msg_type_name, Fore.LIGHTCYAN_EX)

        seqNum = fix.Session.lookupSession(sessionID).getExpectedSenderNum()
        self.session_seqNum[sessionID.toString()] = seqNum

        msg_obj = {
            "time" : Utils.gen_timestamp(),
            "uuid" : Utils.gen_uuid(),
            "state": "SENT",
            "route": msg_route[:-2],
            "type" : f'{msg_type} ({msg_type_name})',
            "msg"  : self.msg_to_str(message),
            "notes": ""
        }

        # Check if a message hes been queued for interception
        # (as this will override the pre-release message)
        try:
            message = Utils.bytes_to_ascii(self.message_queue.peek())
            # If so, change state to intercepted and log it
            msg_obj["state"] = "INTERCEPTED"
            self._log_to_file(sessionID, msg_obj)

            # Then update the message object with the one from the queue which will be logged next
            msg_obj["msg"] = Utils.bytes_to_ascii(self.msg_to_str(message))
            msg_obj["state"] = "SENT"
            msg_obj["notes"] = f"Modified version of {msg_obj['uuid']}"
            msg_obj["uuid"] = Utils.gen_uuid()

        except queue.Empty:
            # If queue is empty we can ignore, as the interceptor wont replace the message
            pass

        # Log the message (this will be the original if not intercepted, or the modified one if intercepted)
        self._log_to_file(sessionID, msg_obj)

        msg_obj["type"] = f"{msg_type} ({msg_type_name_c})"

        # Check if there is a TestReqID field (for Heartbeats during testing)
        try:
            if isinstance(message, str):
                _ = Utils.msg_str_get_field(message, 112)
            else:
                _ = message.getField(fix.TestReqID().getField())

        # If no test found, it is either a regular heartbeat or another message
        except fix.FieldNotFound:
            # If the message is a heartbeat skip (if its heartbeats are being ignored)
            if msg_type in self.ignored_messages:
                return

        # Generate a history ID and append the message log object to the session's message log
        msg_obj["id"] = self._gen_HistoryID(sessionID)
        self.session_message_log[sessionID.toString()].append(msg_obj)

        # Print the message to the console
        prefix = f"{msg_route}S:{session_num} [{str(msg_obj['id']).zfill(5)}] "
        self.msg_print(message, prefix=prefix)

        return


    def _log_to_file(self, sessionID, msg_obj):
        """
        Logs a message object to the session's log file.

        Args:
            sessionID (quickfix.SessionID): The session ID for the log.
            msg_obj (dict): The message object to log.
        """
        msg_obj["time"] = Utils.gen_timestamp()
        log_file = self.session_message_log_file[sessionID.toString()]
        log_entry = ",".join(map(str, msg_obj.values()))

        try:
            with open(f"{log_file}", "a", encoding=F_ENCODING) as f:
                #f.write(f"{log_entry}\n")
                writer = csv.writer(f, escapechar="\\", quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(map(str, msg_obj.values()))

        except (OSError, IOError):
            pass


    def _gen_log_file(self, session_num):
        """
        Initializes a log file for the session.

        Args:
            session_num (str): The session number for which to create the log file.
        """
        sessionID = self._get_sessionID(session_num)
        sess_name = sessionID.toString().replace(":", "-").replace("->", "-")

        log_dir = self.get_session_config(CONFIG_KEYS["FILE_LOG_PATH"], session_num)
        log_id = Utils.gen_timestamp().replace(":","").split(".")[0]
        log_file = f"{log_dir}{log_id}-{sess_name}{LOG_EXT}"

        with open(log_file, "w", encoding=F_ENCODING) as f:
            f.write("Timestamp, UUID, State, Route, Message Type, Message, Notes\n")

        self.session_message_log_file[sessionID.toString()] = log_file


    def has_session(self, session_num, output=False):
        """ Returns True if a specifid session type is active on the client """
        sessionID = self._get_sessionID(session_num)

        if sessionID is not None:
            return True

        if output:
            self.writer.error(
                f"No {session_num.upper()} session"
            )

        return False


    def _get_sessionID(self, session_num):
        """ Returns the session ID based of a specifi session type string """
        try:
            return self.sessions[session_num]["sessionID"]

        except KeyError:
            return None

        return None


    def _get_session_num(self, sessionID):
        """ Returns the session number based on a specific sessionID object """
        for session_num, session in self.sessions.items():
            if sessionID.toString() == session["sessionID"].toString():
                return session_num

        return UNKNOWN


    def _gen_session_config_dict(self, sessionID):
        """ Generates the session configuration dictionaries """
        self.session_config_dict[sessionID.toString()] = {}
        isLoggedOn = fix.Session.lookupSession(sessionID).isLoggedOn()
        self.session_config_dict[sessionID.toString()][LOGGEDON] = isLoggedOn

        for _, value in CONFIG_KEYS.items():
            try:
                data = self.session_settings[sessionID.toString()].getString(value)
                self.session_config_dict[sessionID.toString()][value] = data
            except (KeyError, fix.ConfigError):
                pass


    def get_session_config_dict(self, session_num):
        """ Returns the session configuration dictionary for the specified session type """
        sessionID = self._get_sessionID(session_num)
        self._gen_session_config_dict(sessionID)
        return self.session_config_dict[sessionID.toString()]


    def get_next_seq_num(self, session_num):
        """ Returns the next expected sequence number for the session """
        sessionID = self._get_sessionID(session_num)
        return fix.Session.lookupSession(sessionID).getExpectedSenderNum()


    def get_session_config(self, key, session_num):
        """ Returns the value of a specific session configuration """
        sessionID = self._get_sessionID(session_num)
        try:
            return self.session_settings[sessionID.toString()].getString(key)
        except (KeyError, fix.ConfigError):
            return INVALID


    def set_session_config(self, key, value, session_num):
        """ Sets the value of a specific session configuration """
        sessionID = self._get_sessionID(session_num)
        try:
            if isinstance(value, str):
                self.session_settings[sessionID.toString()].setString(key, value)
            if isinstance(value, int):
                self.session_settings[sessionID.toString()].setInt(key, value)
        except (KeyError, fix.ConfigError):
            pass


    def set_editedMessageFlag(self, session_num, value):
        """ sets the editedMessage flag for the specified session """
        sessionID = self._get_sessionID(session_num)
        self.session_editedMessageFlag[sessionID.toString()] = value


    def set_editedMessage(self, session_num, message):
        """ sets the editedMessage for the specified session """
        sessionID = self._get_sessionID(session_num)
        self.session_editedMessage[sessionID.toString()]  = message


    def set_seq_seed(self, seq_seed):
        """ sets the NextSenderSeqNum to the seed provided """
        self.NextSenderSeqNum = seq_seed


    def set_exp_seq_seed(self, exp_seq_seed):
        """ sets the NextExpSeqNum to the value provided """
        self.NextExpSeqNum = exp_seq_seed


    def set_username(self, username):
        """ Set the applications username value """
        self.username = username


    def get_username(self):
        """ Returns the applications username value """
        return self.username


    def set_password(self, password):
        """ Set the applications password value """
        self.password = password


    def get_password(self):
        """ Returns the applications password value """
        return self.password


    def set_newpassword(self, newpassword):
        """ Set the applications newpassword value """
        self.newpassword = newpassword


    def get_newpassword(self):
        """ Returns the applications newpassword value """
        return self.newpassword


    def get_session_message_log(self, session_num, filter=".*", depth=0):
        """
        Retrieves the message history for a specified session, with optional filtering and depth control.

        Args:
            session_num (str): The session identifier for which the message log is requested.
            filter (str, optional): A regular expression to filter messages based on
            depth (int, optional): The number of most recent messages to retrieve.

        Returns:
            list: A list of messages matching the specified session, filter, and depth criteria.
        """
        sessionID = self._get_sessionID(session_num)
        messages = self.session_message_log[sessionID.toString()]
        filtered_messages = [
            m for m in messages if
                (re.search(fr".*{filter}.*", m['msg'], re.IGNORECASE)
                or
                re.search(fr".*{filter}.*", self.get_message_type(m['msg'])[1],re.IGNORECASE)
            )
        ]
        return filtered_messages[-depth:]

    def _gen_HistoryID(self, sessionID):
        """ Generates a new message ID """
        self.session_message_count[sessionID.toString()] += 1
        return self.session_message_count[sessionID.toString()]


    def _gen_orderID(self):
        """ Generates a new order ID """
        self.orderID = self.orderID+1
        return f"{self.orderID}-{Utils.gen_timestamp(fmt='number')}"


    def _gen_execID(self):
        """ Generates a new execution ID """
        self.execID = self.execID+1
        return f"{self.execID}-{Utils.gen_timestamp(fmt='number')}"


    def _gen_ClOrdID(self):
        """ Generates a new collateralized loan obligation ID """
        self.ClOID = self.ClOID+1
        return f"{self.ClOID}-{Utils.gen_timestamp(fmt='number')}"


    def _gen_MDReqID(self):
        """ Generates a new execution ID """
        self.MDReqID = self.MDReqID+1
        return f"{self.MDReqID}-{Utils.gen_timestamp(fmt='number')}"


    def _gen_QuoteReqID(self):
        """ Generates a new Quote Request ID """
        self.QuoteReqID = self.QuoteReqID+1
        return f"{self.QuoteReqID}-{Utils.gen_timestamp(fmt='number')}"


    def _gen_TestReqID(self):
        """ Generates a new test message ID """
        self.TestReqID = self.TestReqID+1
        return f"{self.TestReqID}-{Utils.gen_timestamp(fmt='number')}"


    def _gen_OrdStatusReqID(self):
        """ Generates a new test message ID """
        self.OrdStatusReqID = self.OrdStatusReqID+1
        return f"{self.OrdStatusReqID}-{Utils.gen_timestamp(fmt='number')}"
