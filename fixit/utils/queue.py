"""
msg_queue.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `PeekableQueue` class, which extends Python's standard `queue.Queue`
    to include a `peek` method. This additional method allows for the inspection of the
    first item in the queue without removing it, enabling non-destructive lookahead operations.

Key Features:
    - Thread-safe peek method: Allows inspection of the first item in the queue
      while maintaining thread safety.
    - Inherits from queue.Queue: Retains all standard queue functionality, including
      blocking and non-blocking operations.

Usage:
    Example of creating and using a `PeekableQueue`:
        ```python
        from msg_queue import PeekableQueue

        queue = PeekableQueue()
        queue.put(1)
        queue.put(2)

        # Peek at the first item without removing it
        first_item = queue.peek()  # Returns 1
        ```
"""

import queue

class PeekableQueue(queue.Queue):
    """
    Adds a thread-safe `peek` method to Python's native `queue.Queue` .

    The `PeekableQueue` class provides all standard functionality of `queue.Queue`,
    including thread-safe operations in addition to a custom `peek` method for
    inspecting the first item in the queue without removing it.

    Attributes:
        Empty (queue.Empty): Exception raised when attempting to peek or retrieve from an empty queue.
        Full (queue.Full): Exception raised when attempting to add to a full queue.
    """
    Empty = queue.Empty
    Full = queue.Full

    def __init__(self, maxsize=0):
        """ Initialize the queue (maxsize 0 = unlimited) """
        super().__init__(maxsize)  # Call the parent constructor


    def peek(self):
        """ Retrieves the first item in the queue without removing it """
        with self.mutex:
            if not self.queue:
                raise queue.Empty

            return self.queue[0]
