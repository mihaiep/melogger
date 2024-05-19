import logging as _logging
import sys
import traceback

from .utils import Levels as _Levels, FORMATS as _FORMATS


# noinspection DuplicatedCode
class Logger(_logging.Logger):
    DIR = "/".join(__file__.split("/")[:-2])

    def debug(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.DEBUG.value).color)})
        super().debug(msg, extra=kwargs)

    def info(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.INFO.value).color)})
        super().info(msg, extra=kwargs)

    def warning(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.WARN.value).color)})
        super().warning(msg, extra=kwargs)

    def warn(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.WARN.value).color)})
        super().warning(msg, extra=kwargs)

    def error(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.ERROR.value).color)})
        super().error(msg, extra=kwargs)

    def exception(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.ERROR.value).color)})
        super().error(msg, extra=kwargs)

    def critical(self, msg, **kwargs):
        self.__set_module_and_function(kwargs)
        kwargs.update({"pref": kwargs.pop("pref", "")})
        kwargs.update({"terminator": kwargs.pop("end", "\n")})
        kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.CRITICAL.value).color)})
        super().critical(msg, extra=kwargs)

    def plain(self, msg, **kwargs):
        """ Print message without any format. """
        if self.isEnabledFor(_Levels.PLAIN.value):
            self.__set_module_and_function(kwargs)
            kwargs.update({"pref": kwargs.pop("pref", "")})
            kwargs.update({"terminator": kwargs.pop("end", "\n")})
            kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.PLAIN.value).color)})
            self._log(_Levels.PLAIN.value, msg, tuple(), extra=kwargs)

    def end_execution(self, **kwargs) -> None:
        if sys.exc_info() != (None, None, None):
            self.critical("Execution ended.")
            self.critical(traceback.format_exc())
            exit(1)
        else:
            self.__set_module_and_function(kwargs)
            kwargs.update({"pref": kwargs.pop("pref", "")})
            kwargs.update({"terminator": kwargs.pop("end", "\n")})
            kwargs.update({"col_start": kwargs.pop("color", _FORMATS.get(_Levels.PLAIN.value).color)})
            super().info("Execution ended.\n\n", extra=kwargs)

    def __set_module_and_function(self, kwargs, depth=3) -> None:
        module, _, function, _ = self.findCaller(False, depth)
        module = module.split("/")[-1].split(".")[0]
        kwargs.update({
            "crt_module": module,
            "crt_method_name": function
        })

    def setLevel(self, level: _Levels | int):
        new_level = level.value if isinstance(level, _Levels) else level
        super().setLevel(new_level)
        for handler in self.handlers:
            handler.setLevel(new_level)
