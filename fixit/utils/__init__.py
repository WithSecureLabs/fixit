"""
Package: utils

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This package provides the utility functions used thoughout the codebase

Exposed Classes:
    - InvalidArgsError from exceptions.py
    - InvalidSessionError from exceptions.py
    - InvalidMsgSpecError from exceptions.py
    - NoActiveMessageError from exception.pt
    - NeedHelpException from exceptions.py
    - Writer from writer.py
    - Utils from common.py
    - SimpleCompleter from parser.py
    - ArgumentParser from parser.py
    - PeekableQueue from queue.py
"""

from .exceptions import InvalidArgsError, InvalidSessionError, InvalidMsgSpecError, NeedHelpException
from .writer import Writer
from .common import Utils
from .parser import SimpleCompleter, ArgumentParser
from .queue import PeekableQueue

__all__ = [
    "InvalidArgsError", "InvalidSessionError", "InvalidMsgSpecError", "NeedHelpEception",
    "NoActiveMessageError", "Writer", "Utils", "SimpleCompleter", "ArgumentParser", "PeekableQueue"
]

