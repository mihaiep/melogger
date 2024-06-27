import logging as _logging
import re
from copy import deepcopy as _deepcopy
from typing import Literal, Mapping, Any

from ._console import _ConsoleFormatter
from ..utils import Levels


class _FileFormatter(_ConsoleFormatter):

    def __init__(self, message_formats: dict, fmt: str = None, date_fmt: str = None, style: Literal["%", "{", "$"] = "%", validate: bool = True, *, defaults: Mapping[str, Any] = None, is_rfh: bool = False):
        self.__is_rfh = is_rfh
        super().__init__(message_formats, fmt, date_fmt, style, validate, defaults=defaults)

    def format(self, message: _logging.LogRecord) -> str:
        if self.__is_rfh is True and not hasattr(message, str(id(message))):
            test_message = self._format(_deepcopy(message))
            setattr(message, str(id(message)), True)
            return test_message
        return super().format(message)

    # noinspection PyTypeChecker
    def custom_format(self, message: _logging.LogRecord) -> None:
        message.col_start, message.col_end = "", ""
        message.msg = re.sub(self.ANSI_REGEX, "", message.msg)
        self.__handle_pref(message)

    # noinspection PyTypeChecker
    def __handle_pref(self, message: _logging.LogRecord) -> None:
        split_cr = message.pref.split('\r')
        if message_cr := len(split_cr) > 1:
            message.pref = f'\r{split_cr[-1]}'

        if self.prev_message is not None:
            prev_new_line = '\n' in self.prev_message.terminator
            if prev_new_line:
                message.pref = message.pref.replace('\r', "")
            elif message_cr:
                message.pref = message.pref.replace('\r', "\n")
            elif message.levelno < Levels.PLAIN.value:
                message.pref = '\n' + message.pref
