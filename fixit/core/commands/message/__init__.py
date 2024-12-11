"""
Package: message

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This package provides tools for managing the fixit applications messaging features

Exposed Classes:
    - Delete (from message_delete.py)
    - Drop (from message_drop.py)
    - Edit (from message_edit.py)
    - Fuzz (from message_fuzz.py)
    - List (from message_list.py)
    - Load (from message_load.py)
    - New (from message_new.py)
    - Save (from message_save.py)
    - Send (from message_send.py)
    - Use (from message_use.py)
    - View (from message_view.py)
"""

from .message_delete import Delete
from .message_drop import Drop
from .message_edit import Edit
from .message_fuzz import Fuzz
from .message_list import List
from .message_load import Load
from .message_save import Save
from .message_new import New
from .message_send import Send
from .message_use import Use
from .message_view import View

__all__ = [
    "Delete", "Drop", "Edit", "Fuzz", "List",
    "Load", "Save", "New", "Send", "Use", "View"
]
