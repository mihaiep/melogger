from enum import Enum as _Enum
from types import MappingProxyType as _MappingProxyType

from .colors import Colors as _Colors


class Levels(_Enum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    CRITICAL = 50
    PLAIN = 60


class LevelData:
    def __init__(self, label: str, color: str, text_format: str):
        self.label = label
        self.color = color
        self.text_format = text_format


# noinspection SpellCheckingInspection
FORMATS = _MappingProxyType({
    Levels.DEBUG.value: LevelData("DEBUG", _Colors.COL.GREY, "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"),
    Levels.INFO.value: LevelData("INFO", _Colors.COL.DEFAULT, "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
    Levels.WARN.value: LevelData("WARN", _Colors.COL.YELLOW, "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
    Levels.ERROR.value: LevelData("ERROR", _Colors.COL.RED, "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d)%(col_end)s %(message)s%(terminator)s"),
    Levels.CRITICAL.value: LevelData("CRITICAL", _Colors.COL.PURE.RED, "%(pref)s%(col_start)s%(asctime)s [%(level_name)s] %(module)s (%(process)d) %(message)s%(col_end)s%(terminator)s"),
    Levels.PLAIN.value: LevelData("PLAIN", _Colors.COL.DEFAULT, "%(pref)s%(col_start)s%(message)s%(col_end)s%(terminator)s")
})
