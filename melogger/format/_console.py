import re

from ._file import _FileFormatter
from ..colors import Colors as _Colors
from ..utils import LevelData as _LevelData


class _ConsoleFormatter(_FileFormatter):
    def custom_format(self, cpy_message, level_data: _LevelData) -> None:
        cpy_message.start = "" if not hasattr(cpy_message, "start") else cpy_message.start
        cpy_message.col_end = _Colors.END
        cpy_message.col_start = level_data.color if not hasattr(cpy_message, 'col_start') else "".join(re.findall(self.ANIS_REGEX, cpy_message.col_start))
