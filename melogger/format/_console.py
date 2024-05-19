import logging as _logging
import os
import re
from copy import copy as _copy
from typing import Literal, Mapping, Any

from melogger.colors import Colors as _Colors
from melogger.utils import Levels


class _ConsoleFormatter(_logging.Formatter):
    LINE_SEP = os.linesep
    ANSI_REGEX = r"\033\[[\d;]*[A-Za-z]"
    _logging.addLevelName(Levels.PLAIN.value, "PLAIN")

    def __init__(self, message_formats: dict, fmt: str = None, date_fmt: str = None, style: Literal["%", "{", "$"] = "%", validate: bool = True, *, defaults: Mapping[str, Any] = None):
        self.level_data = None
        self.FORMATS = message_formats
        super().__init__(fmt, date_fmt, style, validate, defaults=defaults)

    def format(self, message: _logging.LogRecord) -> str:
        _ConsoleFormatter.__validate_pref(message)
        _ConsoleFormatter.__validate_terminator(message)

        cpy_msg = _copy(message)
        if hasattr(cpy_msg, "crt_module"):
            cpy_msg.module = cpy_msg.crt_module
        if hasattr(cpy_msg, "crt_method_name"):
            cpy_msg.funcName = cpy_msg.crt_method_name

        self.level_data = self.FORMATS.get(cpy_msg.levelno)
        cpy_msg.level_name = self.level_data.label
        self.custom_format(cpy_msg)
        return _logging.Formatter(self.level_data.text_format).format(cpy_msg)

    def custom_format(self, message: _logging.LogRecord) -> None:
        message.col_end = _Colors.END
        message.col_start = self.level_data.color if not hasattr(message, "col_start") else "".join(re.findall(self.ANSI_REGEX, message.col_start))

    # noinspection PyUnresolvedReferences
    @staticmethod
    def __validate_pref(message: _logging.LogRecord):
        if hasattr(message, "pref") and len(re.sub(r"[ \t\r]", "", message.pref)) > 0:
            raise ValueError("pref supports only ` `, `\\t` or `\\r`")

    # noinspection PyUnresolvedReferences
    @staticmethod
    def __validate_terminator(message: _logging.LogRecord):
        if hasattr(message, "terminator") and len(re.sub(r"\n", "", message.terminator)) > 0:
            raise ValueError("terminator supports only new line")
