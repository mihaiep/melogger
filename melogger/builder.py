import logging as _logging
import os as _os
import sys as _sys
from logging.handlers import RotatingFileHandler as _RotatingFileHandler
from typing import Union as _Union

from .format import (FileFormatter as _FileFormatter, ConsoleFormatter as _ConsoleFormatter)
from .logger import Logger as _Logger
from .utils import Levels as _Levels, FORMATS as _FORMATS


class LoggerBuilder:
    @staticmethod
    def build(name: str = "LoggerME",
              logs_level: _Union[int, _Levels] = _Levels.INFO,
              formats: dict = _FORMATS,
              terminator: str = "",
              logs_path: str = None,
              file_name: str = None,
              file_terminator: str = "",
              file_mode: str = "a",
              file_enc="utf-8",
              file_backups=5,
              file_max_size=1024 ** 2 * 5) -> _Logger:
        """
        :param name: Logger name
        :param logs_level: Lowest logs level that will be displayed
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
        logger.addHandler(LoggerBuilder.get_console_handler(logs_level, formats=formats, terminator=terminator))
        if file_name:
            logger.addHandler(LoggerBuilder.get_file_handler(file_name, logs_level, formats=formats, logs_path=logs_path, file_terminator=file_terminator, file_mode=file_mode, file_enc=file_enc, file_backups=file_backups, file_max_size=file_max_size))
        logger.setLevel(logs_level)
        return logger

    @staticmethod
    def __setup_handler(handler, formatter, level, terminator):
        handler.setFormatter(formatter)
        handler.setLevel(level.value if isinstance(level, _Levels) else level)
        handler.terminator = terminator
        return handler

    @staticmethod
    def get_console_handler(logs_level: _Union[int, _Levels], *, formats: dict = _FORMATS, terminator: str = ""):
        return LoggerBuilder.__setup_handler(
            handler=_logging.StreamHandler(stream=_sys.stdout),
            formatter=_ConsoleFormatter(formats),
            level=logs_level,
            terminator=terminator
        )

    @staticmethod
    def get_file_handler(file_name: str, logs_level: _Union[int, _Levels], *, formats: dict = _FORMATS,
                         logs_path: str = None, file_terminator: str = "", file_mode: str = "a", file_enc="utf-8",
                         file_backups=5, file_max_size=1024 ** 2 * 5) -> _logging.FileHandler:
        logs_path = logs_path or _os.path.abspath(_os.curdir)
        file_path = _os.path.join(logs_path, file_name)
        if not _os.path.isdir(logs_path):
            _os.mkdir(logs_path)
        kwargs = {
            "filename": file_path,
            "mode": file_mode,
            "encoding": file_enc
        }
        if file_mode == "a":
            kwargs.update({
                "backupCount": file_backups,
                "maxBytes": file_max_size
            })
        return LoggerBuilder.__setup_handler(
            handler=_RotatingFileHandler(**kwargs),
            formatter=_FileFormatter(formats, is_rfh=file_max_size is not None and file_max_size > 0),
            level=logs_level,
            terminator=file_terminator
        )

    @staticmethod
    def remove_handlers(logger, _filter):
        for handler in list(logger.handlers):
            if _filter(handler):
                logger.handlers.remove(handler)
