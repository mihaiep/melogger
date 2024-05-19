import logging as _logging
import re
from typing import Literal, Mapping, Any

from ._console import _ConsoleFormatter
from ..utils import Levels


class _FileFormatter(_ConsoleFormatter):

    def __init__(self, message_formats: dict, fmt: str = None, date_fmt: str = None, style: Literal["%", "{", "$"] = "%", validate: bool = True, *, defaults: Mapping[str, Any] = None):
        self.prev_message = None
        super().__init__(message_formats, fmt, date_fmt, style, validate, defaults=defaults)

    # noinspection PyTypeChecker
    def custom_format(self, message: _logging.LogRecord) -> None:
        self.__handle_pref(message)
        # Remove colors
        message.col_start, message.col_end = "", ""
        message.msg = re.sub(self.ANSI_REGEX, "", message.msg)

    # noinspection PyTypeChecker
    def __handle_pref(self, message: _logging.LogRecord) -> None:
        after_cr = re.findall('\r(.*)', message.pref)
        after_cr = after_cr[-1] if len(after_cr) > 0 else message.pref
        if self.prev_message is None:
            message.pref = after_cr
        elif message.levelno < Levels.PLAIN.value:
            message.pref = ("" if "\n" in self.prev_message.terminator else "\n") + after_cr
        elif '\r' in message.pref and '\n' in self.prev_message.terminator:
            message.pref = f'{after_cr}'
        elif '\r' in message.pref and '\n' not in self.prev_message.terminator:
            message.pref = f'\n{after_cr}'
        self.prev_message = message
