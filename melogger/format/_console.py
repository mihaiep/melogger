import logging as _logging
import os
import re
from copy import deepcopy as _deepcopy
from typing import Literal, Mapping, Any

from melogger.colors import Colors as _Colors
from melogger.utils import Levels


class _ConsoleFormatter(_logging.Formatter):
    LINE_SEP = os.linesep
    ANSI_REGEX = r"\033\[[\d;]*[A-Za-z]"
    _logging.addLevelName(Levels.PLAIN.value, "PLAIN")

    def __init__(self, message_formats: dict, fmt: str = None, date_fmt: str = None, style: Literal["%", "{", "$"] = "%", validate: bool = True, *, defaults: Mapping[str, Any] = None):
        self.level_data = None
        self.prev_message = None
        self.FORMATS = message_formats
        super().__init__(fmt, date_fmt, style, validate, defaults=defaults)

    def format(self, message: _logging.LogRecord) -> str:
        formatted_message = self._format(_deepcopy(message))
        self.prev_message = message
        return formatted_message

    def _format(self, message: _logging.LogRecord) -> str:
        _ConsoleFormatter.__validate_pref(message)
        _ConsoleFormatter.__validate_terminator(message)

        if hasattr(message, "crt_module"):
            message.module = message.crt_module
        if hasattr(message, "crt_method_name"):
            message.funcName = message.crt_method_name

        self.level_data = self.FORMATS.get(message.levelno)
        message.level_name = self.level_data.label
        self.custom_format(message)
        return _logging.Formatter(self.level_data.text_format).format(message)

    def custom_format(self, message: _logging.LogRecord) -> None:
        message.col_end = _Colors.END
        message.col_start = self.level_data.color if not hasattr(message, "col_start") else "".join(re.findall(self.ANSI_REGEX, message.col_start))
        if self.prev_message is not None and message.levelno < Levels.PLAIN.value and '\r' not in message.prefix and '\n' not in self.prev_message.terminator:
            message.prefix = '\n' + message.prefix

    # noinspection PyUnresolvedReferences
    @staticmethod
    def __validate_pref(message: _logging.LogRecord):
        if hasattr(message, "prefix") and len(re.sub(r"[ \t\r]", "", message.prefix)) > 0:
            raise ValueError("prefix supports only ` `, `\\t` or `\\r`")

    # noinspection PyUnresolvedReferences
    @staticmethod
    def __validate_terminator(message: _logging.LogRecord):
        if hasattr(message, "terminator") and len(re.sub(r"\n", "", message.terminator)) > 0:
            raise ValueError("terminator supports only new line")
