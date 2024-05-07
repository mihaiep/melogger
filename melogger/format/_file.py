import re as _re

from ._console import _ConsoleFormatter
from ..utils import Levels, LevelData as _LevelData


class _FileFormatter(_ConsoleFormatter):

    def custom_format(self, cpy_message, level_data: _LevelData) -> None:
        cpy_message.start = (
            "" if not hasattr(cpy_message, "start") else
            cpy_message.start.replace("\r", "\n") if cpy_message.levelno < Levels.PLAIN.value else
            cpy_message.start
        )
        # Remove colors
        cpy_message.col_start, cpy_message.col_end = "", ""
        cpy_message.msg = _re.sub(self.ANSI_REGEX, "", cpy_message.msg.strip())
