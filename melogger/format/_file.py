import logging as _logging
import re as _re
from copy import copy as _copy

from ..utils import Levels, LevelData as _LevelData


class _FileFormatter(_logging.Formatter):
    LINE_SEP = "\n"
    ANIS_REGEX = r"\033\[[\d;]*[A-Za-z]"
    _logging.addLevelName(Levels.PLAIN.value, "PLAIN")
    FORMATS = {}

    def format(self, message) -> str:
        cpy_msg = _copy(message)
        level_data = self.FORMATS.get(cpy_msg.levelno)
        cpy_msg.levelname = level_data.label
        if hasattr(cpy_msg, 'crt_module'):
            cpy_msg.module = cpy_msg.crt_module
        if hasattr(cpy_msg, 'crt_method_name'):
            cpy_msg.funcName = cpy_msg.crt_method_name
        cpy_msg.terminator = cpy_msg.end if hasattr(cpy_msg, 'end') else self.LINE_SEP
        self.custom_format(cpy_msg, level_data)
        return _logging.Formatter(level_data.text_format).format(cpy_msg)

    def custom_format(self, cpy_message, level_data: _LevelData) -> None:
        cpy_message.start = "" if not hasattr(cpy_message, "start") else \
            cpy_message.start.replace("\r", "\n") if cpy_message.levelno < Levels.PLAIN.value else \
                cpy_message.start
        cpy_message.col_start = ""
        cpy_message.col_end = ""
        # Remove colors
        cpy_message.msg = _re.sub(self.ANIS_REGEX, "", cpy_message.msg)
