"""
exceptions.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines custom exceptions used within the Fixit application. These
    exceptions are tailored to handle specific error scenarios encountered during
    command execution, session validation, message specification parsing, and argument
    parsing.

Key Features:
    - Custom exceptions tailored to the Fixit application.
    - Descriptive error messages for improved debugging and user feedback.
    - Consistent structure for initialization and string representation of exceptions.

Usage:
    These custom exceptions are used throughout the Fixit application to handle errors
    gracefully. Example:
        ```python
        if not valid_args:
            raise InvalidArgsError("Expected arguments are missing")
        ```
"""

class InvalidArgsError(Exception):
    """ Raised when command arguments are invalid or missing """
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args if args else None

    def __str__(self):
        if self.message:
            return f"InvalidArgsError, {self.message}"

        return "InvalidArgsError raised"


class InvalidSessionError(Exception):
    """Raised when a session is invalid """
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args if args else None

    def __str__(self):
        if self.message:
            return f"InvalidSessionError, {self.message}"

        return "InvalidSessionError raised"


class InvalidMsgSpecError(Exception):
    """Raised when a message specification is invalid """
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args if args else None

    def __str__(self):
        if self.message:
            return f"InvalidMsgSpecError, {self.message}"

        return "InvalidMsgSpecError raised"


class NoActiveMessageError(Exception):
    """Raised when a message is missing from the message context """
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args if args else None

    def __str__(self):
        if self.message:
            return f"NoActiveMessageError, {self.message}"

        return "NoActiveMessageError raised"


class NeedHelpException(Exception):
    """Raised when commad help is needed during argumetn parsing"""
    def __init__(self, *args):
        super().__init__(*args)
        self.message = args if args else None

    def __str__(self):
        if self.message:
            return f"NeedHelpException, {self.message}"

        return "NeedHelpException raised"
