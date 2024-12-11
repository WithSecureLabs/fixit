"""
constants.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines all constant variables that are shared across the various modules
    that constitute the Fixit application. These constants provide configuration values,
    fixed options, and utility definitions required for the application's operation.

Exposed Constants:
    APP_NAME (str): Name of the application.
    VERSION (str): Current version of the application.
    DESCRIPTON (str): Brief description of the application.
    EXAMPLE (str): Example command-line usage of the application.
    BANNER (str): ASCII art banner displayed on application startup.
    OPT_VAL, OPT_DESC (str): Keys for option values and descriptions in configuration dictionaries.
    CONST_DIRS (list): List of required directories for logs, messages, and output.
    CONFIG_KEYS (dict): Keys used for FIX session configuration, referencing QuickFIX standards.
    FIX_HEAD_FIELDS (list): List of FIX protocol header field tags.
    POLL_TIME (float): Default time interval for polling during logon / logout.
    RESP_DELAY, FUZZ_DELAY (dict): Mutable defaults for response and fuzzing delays.
    COLOR CONSTANTS: Fore.RED, Fore.BLUE, Fore.GREEN, Fore.YELLOW for CLI output styling.
    SESSION_TYPES (list): Supported session types for FIX interactions.
    LOG_EXT (str): Default file extension for message logs.
    ERR_MSG, ERR_MSG_MR00, ERR_MSG_CM01 (str): Predefined error messages.

Usage:
    This module is intended to be imported into other modules in the Fixit application,
    providing shared constants and configuration values to maintain consistency across the codebase.
"""

import sys
from colorama import Fore

APP_NAME = "Fixit"

VERSION = "0.1"

DESCRIPTON = "CLI Application for interfacing with a FIX Gateway"

EXAMPLE = (
    "Example usage:\n"
    f"  python {sys.argv[0]} ./config/initiator.cfg --colour --preload \\"
    '\n  "message new ORD-BUY" "message edit 38=100" "message send" "exit"'
    "\n "
)

BANNER = """
    ___________  __ __________
   / ____/  _/ |/ //  _/_  __/
  / /_   / / |   / / /  / /
 / __/ _/ / /   |_/ /  / /
/_/   /___//_/|_/___/ /_/"""

OPT_VAL = "VAL"
OPT_DESC = "DESC"

NIG_TYPE = "NUMINGROUP"
UNKNOWN = "UNKNOWN"
INVALID = "INVALID"
MISSING = "MISSING"
LOGGEDON = "LoggedOn"

SOH_BIN = "\x01"
SOH_UNI = {"value": "|"} # Using dict so it is mutable

DELIM_BIN = "\x3D"
DELIM_UNI = "="

TAB = " "*4

YES = "YES"
NO = "NO"
ALL = "ALL"
YES_ALL = f"{YES}_{ALL}"
NO_ALL = f"{NO}_{ALL}"

ADM_F, APP_F = "ADM", "APP"
IN, OUT = "<-", "->"
ADM_I = f"{IN} IN ({ADM_F}): "
ADM_O = f"{OUT} OUT({ADM_F}): "
APP_I = f"{IN} IN ({APP_F}): "
APP_O = f"{OUT} OUT({APP_F}): "

RAW = "RAW"

DEFAULT_LOGON_TIMEOUT = 10
DEFAULT_LOGOUT_TIMEOUT = 2
DEFAULT_RECONNECT_INTERVAL = 30

LOG_DIR = "./logs/"
MSG_DIR = "./messages/"
OUT_DIR = "./output/"
SPEC_DIR= "./fixit/specs/"
CONST_DIRS = [LOG_DIR, MSG_DIR, OUT_DIR, SPEC_DIR]

TYPE_QUOTE = "QUOTE"
TYPE_TRADE = "TRADE"
SESSION_TYPES = [TYPE_QUOTE, TYPE_TRADE]

LOG_EXT = ".fixit.message.log"

ARGS_SESSION_DESC = "The FIX session to use"
ARGS_ACTION_DESC = "The command action to run"

CMD_VARIABLE = "VARIABLE"
CMD_STATIC = "STATIC"

MANUAL_RECON_INT = 0

ERR_MSG = "Invalid message"
ERR_MSG_MR00 = "ERR-MR00"
ERR_MSG_MR01 = "ERR-MR01"
ERR_MSG_CM01 = "ERR-CM01"

RED = Fore.RED
BLUE = Fore.BLUE
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW

TARGET_FLAG = "¬¬REPLACE_ME¬¬"

F_ENCODING = "utf-8"
M_ENCODING = "utf-8"

POLL_TIME = 0.1
RESP_DELAY = {"value": 0.1} # Using dict so it is mutable
FUZZ_DELAY = {"value": 0.05} # Using dict so it is mutable

FIX_HEAD_FIELDS = [
    8, 9, 35, 49, 56, 115, 128, 90, 91, 34,
    50, 142, 57, 143, 116, 114, 129, 145, 43
]

# ref: https://www.quickfixj.org/usermanual/2.3.0/usage/configuration.html
CONFIG_KEYS = {
    "BEGINSTRING": "BeginString",
    "SENDERCOMPID": "SenderCompID",
    "SENDERSUBID": "SenderSubID",
    "SENDERLOCID": "SenderLocationID",
    "TARGETCOMPID": "TargetCompID",
    "TARGETSUBID": "TargetSubID",
    "TARGETLOCID": "TargetLocationID",
    "SESSION_QUALIFIER": "SessionQualifier",
    "DEFAULT_APPLVERID": "DefaultApplVerID",
    "CONNECTION_TYPE": "ConnectionType",
    "USE_DATA_DICTIONARY": "UseDataDictionary",
    "NON_STOP_SESSION": "NonStopSession",
    "USE_LOCAL_TIME": "UseLocalTime",
    "TIME_ZONE": "TimeZone",
    "START_DAY": "StartDay",
    "END_DAY": "EndDay",
    "START_TIME": "StartTime",
    "END_TIME": "EndTime",
    "HEARTBTINT": "HeartBtInt",
    "SOCKET_ACCEPT_HOST": "SocketAcceptHost",
    "SOCKET_ACCEPT_PORT": "SocketAcceptPort",
    "SOCKET_CONNECT_HOST": "SocketConnectHost",
    "SOCKET_CONNECT_PORT": "SocketConnectPort",
    "RECONNECT_INTERVAL": "ReconnectInterval",
    "FILE_LOG_PATH": "FileLogPath",
    "DEBUG_FILE_LOG_PATH": "DebugFileLogPath",
    "FILE_STORE_PATH": "FileStorePath",
    "REFRESH_ON_LOGON": "RefreshOnLogon",
    "RESET_ON_LOGON": "ResetOnLogon",
    "RESET_ON_LOGOUT": "ResetOnLogout",
    "RESET_ON_DISCONNECT": "ResetOnDisconnect",
    "VALIDATE_FIELDS_OUT_OF_ORDER": "ValidateFieldsOutOfOrder",
    "VALIDATE_FIELDS_HAVE_VALUES": "ValidateFieldsHaveValues",
    "VALIDATE_USER_DEFINED_FIELDS": "ValidateUserDefinedFields",
    "VALIDATE_LENGTH_AND_CHECKSUM": "ValidateLengthAndChecksum",
    "ALLOW_UNKNOWN_MSG_FIELDS": "AllowUnknownMsgFields",
    "DATA_DICTIONARY": "DataDictionary",
    "TRANSPORT_DATA_DICTIONARY": "TransportDataDictionary",
    "APP_DATA_DICTIONARY": "AppDataDictionary",
    "PERSIST_MESSAGES": "PersistMessages",
    "LOGON_TIMEOUT": "LogonTimeout",
    "LOGOUT_TIMEOUT": "LogoutTimeout",
    "SEND_REDUNDANT_RESENDREQUESTS": "SendRedundantResendRequests",
    "RESEND_SESSION_LEVEL_REJECTS": "ResendSessionLevelRejects",
    "MILLISECONDS_IN_TIMESTAMP": "MillisecondsInTimeStamp",
    "TIMESTAMP_PRECISION": "TimeStampPrecision",
    "ENABLE_LAST_MSG_SEQ_NUM_PROCESSED": "EnableLastMsgSeqNumProcessed",
    "MAX_MESSAGES_IN_RESEND_REQUEST": "MaxMessagesInResendRequest",
    "SEND_LOGOUT_BEFORE_TIMEOUT_DISCONNECT": "SendLogoutBeforeDisconnectFromTimeout",
    "SOCKET_NODELAY": "SocketNodelay",
    "SOCKET_SEND_BUFFER_SIZE": "SocketSendBufferSize",
    "SOCKET_RECEIVE_BUFFER_SIZE": "SocketReceiveBufferSize",
    "SOCKET_SEND_TIMEOUT": "SocketSendTimeout",
    "SOCKET_RECEIVE_TIMEOUT": "SocketReceiveTimeout",
    "IGNORE_POSSDUP_RESEND_REQUESTS": "IgnorePossDupResendRequests",
    "RESETSEQUENCE_MESSAGE_REQUIRES_ORIGSENDINGTIME": "RequiresOrigSendingTime",
    "CHECK_LATENCY": "CheckLatency",
    "MAX_LATENCY": "MaxLatency",
    "SSL_ENABLE": "SSLEnable",
    "SSL_SERVERNAME": "SSLServerName",
    "SSL_PROTOCOLS": "SSLProtocols",
    "SSL_VALIDATE_CERTIFICATES": "SSLValidateCertificates",
    "SSL_CHECK_CERTIFICATE_REVOCATION": "SSLCheckCertificateRevocation",
    "SSL_CERTIFICATE": "SSLCertificate",
    "SSL_CERTIFICATE_PASSWORD": "SSLCertificatePassword",
    "SSL_REQUIRE_CLIENT_CERTIFICATE": "SSLRequireClientCertificate",
    "SSL_CA_CERTIFICATE": "SSLCACertificate",
}
