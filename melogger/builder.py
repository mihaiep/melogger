import logging as _logging
import os as _os
import sys as _sys
from logging.handlers import RotatingFileHandler as _RotatingFileHandler
from typing import Union as _Union

from .format._console import _ConsoleFormatter
from .format._file import _FileFormatter
from .logger import Logger as _Logger
from .utils import Levels as _Levels, FORMATS as _FORMATS


class LoggerBuilder:
    __logger = None

    @staticmethod
    def get_logger(name: str = "LoggerME", level: _Union[int, _Levels] = _Levels.INFO, formats: dict = _FORMATS, terminator: str = "",
                   logs_path: str = None, file_name: str = None, file_terminator: str = "", file_mode: str = 'a',
                   file_enc='utf-8', file_backups=5, file_max_size=1024 ** 2 * 5) -> _Logger:
        """
        :param name: Logger name
        :param level: Lowest logs level that will be displayed
        :param formats: A dict to describe the format for each log level
        :param terminator: end line character
        :param logs_path: path where logs are going be stored
        :param file_name: logs file name
        :param file_terminator: end line character for files
        :param file_mode: open mode - same as open(...,mode=<mode>) - setting it to 'w' will make file handler to ignore file_backups and file_max_size
        :param file_enc: encoding for file
        :param file_backups: number of replicas
        :param file_max_size: max size of a file
        :return: Logger
        """
        if LoggerBuilder.__logger is None:
            _ConsoleFormatter.FORMATS = formats
            _FileFormatter.FORMATS = formats

            LoggerBuilder.__logger = _Logger(name)

            ch = _logging.StreamHandler(stream=_sys.stdout)
            ch.setFormatter(_ConsoleFormatter())
            ch.setLevel(level.value if isinstance(level, _Levels) else level)
            ch.terminator = terminator
            LoggerBuilder.__logger.addHandler(ch)

            if file_name:
                if not logs_path:
                    logs_path = _os.path.abspath(_os.curdir)
                if not _os.path.isdir(logs_path):
                    _os.mkdir(logs_path)
                file_path = _os.path.join(logs_path, file_name)
                _sys.stdout.write(f"Start logging into: {file_path}{_os.linesep}")
                fh = _RotatingFileHandler(filename=file_path, mode=file_mode, encoding=file_enc) if file_mode == 'w' else \
                     _RotatingFileHandler(filename=file_path, mode=file_mode, encoding=file_enc, backupCount=file_backups,maxBytes=file_max_size)
                fh.setFormatter(_FileFormatter())
                fh.setLevel(level.value if isinstance(level, _Levels) else level)
                fh.terminator = file_terminator
                LoggerBuilder.__logger.addHandler(fh)
            LoggerBuilder.__logger._Logger__start_execution()
        return LoggerBuilder.__logger
