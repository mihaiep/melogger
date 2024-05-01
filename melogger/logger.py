import logging as _logging
import os as _os
from typing import Union

from .colors import Colors as _Colors
from .utils import Levels as _Levels


class Logger(_logging.Logger):
    DIR = "/".join(__file__.split("/")[:-2])

    def info_green(self, msg: str, *args, **kwargs):
        """Force next INFO log to be green"""
        module, function = self.__get_module_and_function()
        self.info(msg, *args, **kwargs, extra={'col_start': _Colors.COL.GREEN, 'crt_module': module, 'crt_method_name': function})

    def info_color(self, msg: str, color: str, *args, **kwargs):
        """Allows to set a color for next INFO log message"""
        module, function = self.__get_module_and_function()
        self.info(msg, *args, **kwargs, extra={'col_start': color, 'crt_module': module, 'crt_method_name': function})

    def plain(self, msg, color: str = None, end: str = _os.linesep, *args, **kwargs):
        """Print message without any format. \n
        Color - change the color for next message\n
        end - end line character override for next message"""
        if self.isEnabledFor(_Levels.PLAIN.value):
            module, function = self.__get_module_and_function()
            extra = {'crt_module': module, 'crt_method_name': function, 'end': end}
            if color is not None:
                extra['col_start'] = color
            self._log(_Levels.PLAIN.value, msg, args, **kwargs, extra=extra)

    def __start_execution(self, message: str = None):
        module, function = self.__get_module_and_function(4)
        message = message if message is not None else "Execution started"
        self.info(message, extra={'col_start': _Colors.COL.GREEN, 'crt_module': module, 'crt_method_name': function})

    def end_execution(self) -> None:
        import sys
        if sys.exc_info() != (None, None, None):
            import traceback
            self.critical("Execution ended.")
            self.critical(traceback.format_exc())
            exit(1)
        else:
            color = _Colors.COL.DEFAULT
            module, function = self.__get_module_and_function()
            self.info("Execution ended.\n\n", extra={'col_start': color, 'cmodule': module, 'cfuncName': function})

    def __get_module_and_function(self, depth=3) -> [str, str]:
        module, _, function, _ = self.findCaller(False, depth)
        module = module.split("/")[-1].split(".")[0]
        return module, function

    def setLevel(self, level: Union[_Levels, int]):
        super().setLevel(level.value if isinstance(level, _Levels) else level)
