import logging as _logging
import os as _os
import sys as _sys
from logging.handlers import RotatingFileHandler as _RotatingFileHandler
from typing import Union as _Union

from .colors import Colors as _Colors
from .format import (FileFormatter as _FileFormatter, ConsoleFormatter as _ConsoleFormatter)
from .logger import Logger as _Logger
from .utils import Levels as _Levels, FORMATS as _FORMATS


class LoggerBuilder:
    @staticmethod
    def build(name: str = "LoggerME", level: _Union[int, _Levels] = _Levels.INFO, formats: dict = _FORMATS, terminator: str = "",
              logs_path: str = None, file_name: str = None, file_terminator: str = "", file_mode: str = "a",
              file_enc="utf-8", file_backups=5, file_max_size=1024 ** 2 * 5) -> _Logger:
        """
        :param name: Logger name
        :param level: Lowest logs level that will be displayed
        :param formats: A dict to describe the format for each log level
        :param terminator: end line character
        :param logs_path: path where logs are going be stored
        :param file_name: logs file name
        :param file_terminator: end line character for files
        :param file_mode: open mode - same as open(...,mode=<mode>) - setting it to "w" will make file handler to ignore file_backups and file_max_size
        :param file_enc: encoding for file
        :param file_backups: number of replicas
        :param file_max_size: max size of a file
        :return: Logger
        """
        logger = _Logger(name)
        logger.setLevel(level)
        LoggerBuilder.add_console_handler(logger, level, formats, terminator)
        if file_name:
            LoggerBuilder.add_file_handler(name, logger, level, formats, logs_path, file_name, file_terminator, file_mode, file_enc, file_backups, file_max_size)
        logger.info(f"Logger {_Colors.COL.GREEN}'{name}'{_Colors.END} started")
        return logger

    @staticmethod
    def __setup_handler(handler, formatter, level, terminator):
        handler.setFormatter(formatter)
        handler.setLevel(level.value if isinstance(level, _Levels) else level)
        handler.terminator = terminator
        return handler

    @staticmethod
    def add_console_handler(logger: _Logger, level: _Union[int, _Levels] = _Levels.INFO, formats: dict = _FORMATS, terminator: str = "", remove_handlers: bool = False):
        ch = LoggerBuilder.__setup_handler(
            handler=_logging.StreamHandler(stream=_sys.stdout),
            formatter=_ConsoleFormatter(formats),
            level=level,
            terminator=terminator
        )
        LoggerBuilder.__finalize_setup(logger, ch, _logging.StreamHandler, remove_handlers)

    @staticmethod
    def add_file_handler(name: str, logger: _Logger, file_level: _Union[int, _Levels] = _Levels.INFO, file_formats: dict = _FORMATS,
                         logs_path: str = None, file_name: str = None, file_terminator: str = "", file_mode: str = "a",
                         file_enc="utf-8", file_backups=5, file_max_size=1024 ** 2 * 5, remove_handlers: bool = False):
        if not logs_path:
            logs_path = _os.path.abspath(_os.curdir)
        if not _os.path.isdir(logs_path):
            _os.mkdir(logs_path)
        file_path = _os.path.join(logs_path, file_name)
        _sys.stdout.write(f"{_Colors.hex('088888')}\"{name}\" will start logging into: {file_path}{_Colors.END}{_os.linesep}{_os.linesep}")
        kwargs = {
            "filename": file_path,
            "mode": file_mode,
            "encoding": file_enc
        }
        kwargs.update({"backupCount": file_backups, "maxBytes": file_max_size} if file_mode == "a" else {})
        fh = LoggerBuilder.__setup_handler(
            handler=_RotatingFileHandler(**kwargs),
            formatter=_FileFormatter(file_formats),
            level=file_level,
            terminator=file_terminator
        )
        LoggerBuilder.__finalize_setup(logger, fh, _logging.FileHandler, remove_handlers)

    @staticmethod
    def __finalize_setup(logger, new_handler, handler_type, remove_handlers):
        if remove_handlers:
            for handler in list(logger.handlers):
                if isinstance(handler, handler_type):
                    logger.handlers.remove(handler)
        logger.addHandler(new_handler)
