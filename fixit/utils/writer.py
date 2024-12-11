"""
writer.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `Writer` class, which handles all console output for the Fixit application.
    It provides utilities for printing formatted text, handling colors, displaying tables, clearing
    the terminal, and prompting for user input.

Key Features:
    - Categorized Output: Supports categories like "INFO", "ERROR", and "WARNING" with formatting.
    - Color and Formatting: Provides color-coded and styled text using the `colorama` library.
    - Table Display: Formats and prints data in a table format using the `tabulate` library.
    - User Prompts: Supports interactive user input with preloaded command handling.
    - Terminal Management: Includes methods for clearing the console and fitting text on screen.

Usage:
    Example of creating a `Writer` instance and printing messages:
        ```python
        writer = Writer(colour_mode=True)
        writer.info("Application started successfully.")
        writer.error("An error occurred during execution.")
        writer.warning("This action might have unintended consequences.")
        ```
    Example of displaying a table:
        ```python
        data = [["Row1", "Data1"], ["Row2", "Data2"]]
        writer.table(data, headers=["Row", "Details"], title="Sample Table")
        ```
"""

import os
import shlex
import readline
import colorama

from colorama import Fore, Style
from tabulate import tabulate

from fixit.utils.exceptions import InvalidArgsError

class Writer():
    """
    Handles formatted console output and user interaction for the Fixit application.

    The `Writer` class provides methods for printing categorized and colorized text,
    displaying data in tables, prompting for user input, and managing terminal output.

    Attributes:
        CATEGORIES (dict): Prefixes for categorized messages (e.g., INFO, ERROR).
        colour_mode (bool): Whether color output is enabled.
        mute (bool): If True, suppresses all console output.
    """
    CATEGORIES = {
        "NORMAL" : "",
        "ERROR"  : "[!] ",
        "INFO"   : "[+] ",
        "WARNING": "[?] ",
    }

    def __init__(self, colour_mode=False):
        colorama.init(autoreset=True)
        self.colour_mode = colour_mode
        tabulate.PRESERVE_WHITESPACE = True
        self.mute = False


    def print(self, text, fmt=Style.NORMAL, limit=False):
        """
        Prints text to the console with optional formatting and length limiting.

        Args:
            text (str): The text to print.
            fmt (str, optional): Formatting style (e.g., color, bold). Defaults to Style.NORMAL.
            limit (bool, optional): If True, truncate the text length to fit the terminal width.
        """
        if limit:
            text = self.limit(text)

        if not self.mute:
            print(self.colour(text, fmt))


    def text(self, text="", fmt=Style.NORMAL, limit=False, cat="NORMAL"):
        """
        Prints formatted and categorized text.

        Args:
            text (str, optional): The text to print. Defaults to an empty string.
            fmt (str, optional): Formatting style (e.g., color, bold). Defaults to Style.NORMAL.
            limit (bool, optional): If True, limits the text length to fit the terminal width. Defaults to False.
            cat (str, optional): Category of the text (e.g., INFO, ERROR). Defaults to "NORMAL".
        """
        text = self.categorise(text, cat)
        self.print(text, fmt, limit)


    def error(self, text):
        """ Prints and returns an error message in redcategory. """
        text = self.categorise(text, "ERROR")
        text = self.colour(text, Fore.RED)
        self.print(text)
        return text


    def info(self, text):
        """ Prints and returns an info message in green. """
        text = self.categorise(text, "INFO")
        text = self.colour(text, Fore.GREEN)
        self.print(text)
        return text


    def warning(self, text):
        """ Prints and returns a warning message in red. """
        text = self.categorise(text, "WARNING")
        text = self.colour(text, Fore.YELLOW)
        self.print(text)
        return text


    def title(self, text):
        """ Prints the provided text in a custom Title format """
        self.print(f"\n{text}")
        self.print(f"{'='*len(text)}\n")


    def clear(self):
        """ Clears the terminal window """
        os.system("cls" if os.name == "nt" else "clear")


    def prompt(self, text=">", fmt=Style.NORMAL, preload_input=None):
        """
        Prompts the user for input.

        Args:
            text (str, optional): The prompt text. Defaults to ">".
            fmt (str, optional): Formatting style for the prompt. Defaults to Style.NORMAL.
            preload_input (list, optional): Flags the prompt as a preloaded command, skipping interaction.

        Returns:
            list: Split user input or preloaded command value.
        """
        try:
            if preload_input is not None and len(preload_input) > 0:
                return self._process_preloaded(text, fmt, preload_input)

            return self.split(input(self.colour(text, fmt)))

        except ValueError as e:
            self.error(str(e))


    def _process_preloaded(self, text, fmt, preload_input):
        """
        Processes the input for preloaded CLI commands.

        Args:
            text (str): The prompt text.
            fmt (str): Formatting style for the prompt.
            preload_input (list): Preloaded command strings.

        Returns:
            list: Split preloaded input.
        """
        readline.add_history(preload_input[0])
        user_input = self.split(preload_input[0])
        self.print(
            f"{self.colour(text, fmt)}"
            f"{self.colour(preload_input[0])}"
        )

        return user_input


    def split(self, text):
        """ Split user input like command line arguments """
        return shlex.split(text)


    def limit(self, text, margin=0):
        """
        Returns the provided text truncated to fit within the current terminal width.

        Args:
            text (str): The text to limit.
            margin (int, optional): Extra space to leave at the end of the line. Defaults to 0.

        Returns:
            str: The truncated text, with "..." appended if it exceeds the limit.
        """
        width = int(os.popen("stty size", "r").read().split()[1]) - 3 - margin
        return text if len(text) < width else text[:width]+"..."


    def colour(self, text, fmt=Style.NORMAL):
        """ Returns text formatted in a specified colour """
        if self.colour_mode:
            return f"{fmt}{text}{Style.RESET_ALL}"

        return text


    def categorise(self, text, cat="NORMAL"):
        """ Returns the provided text with a category marker prepended. """
        prefix = self.CATEGORIES[cat]
        if text.startswith("\n"):
            text = text[1:]
            prefix = f"\n{self.CATEGORIES[cat]}"

        return f"{prefix}{text}"


    def table(self, table, headers=None, title=None):
        """
        Prints and returns the provided data in a table format.

        Args:
            table (list): The data to display as a table.
            headers (list, optional): Column headers. Defaults to None.
            title (str, optional): The title of the table. Defaults to None.

        Returns:
            str: The table as a plain-text string.
        """
        if headers is None:
            headers = []

        if title is not None:
            self.title(title)

        self.print(tabulate(table, headers=headers))

        return tabulate(table, headers=headers, tablefmt="plain")
