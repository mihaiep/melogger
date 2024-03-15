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
        logger = _Logger(name)
        LoggerBuilder.setup_console_handler(logger, level, formats, terminator)
        if file_name: LoggerBuilder.setup_file_handler(logger, level, formats, logs_path, file_name, file_terminator, file_mode, file_enc, file_backups, file_max_size)
        logger._Logger__start_execution()
        return logger

    @staticmethod
    def setup_console_handler(logger: _Logger, level: _Union[int, _Levels] = _Levels.INFO, formats: dict = _FORMATS, terminator: str = "", remove_handlers: bool = False):
        ch = _logging.StreamHandler(stream=_sys.stdout)
        ch.setFormatter(_ConsoleFormatter(formats))
        ch.setLevel(level.value if isinstance(level, _Levels) else level)
        ch.terminator = terminator
        LoggerBuilder.__finalize_setup(logger, ch, _logging.StreamHandler, remove_handlers)

    @staticmethod
    def setup_file_handler(logger: _Logger, file_level: _Union[int, _Levels] = _Levels.INFO, file_formats: dict = _FORMATS,
                           logs_path: str = None, file_name: str = None, file_terminator: str = "", file_mode: str = 'a',
                           file_enc='utf-8', file_backups=5, file_max_size=1024 ** 2 * 5, remove_handlers: bool = False):
        if not logs_path:
            logs_path = _os.path.abspath(_os.curdir)
        if not _os.path.isdir(logs_path):
            _os.mkdir(logs_path)
        file_path = _os.path.join(logs_path, file_name)
        _sys.stdout.write(f"Start logging into: {file_path}{_os.linesep}")
        fh = _RotatingFileHandler(filename=file_path, mode=file_mode, encoding=file_enc) if file_mode == 'w' else \
            _RotatingFileHandler(filename=file_path, mode=file_mode, encoding=file_enc, backupCount=file_backups, maxBytes=file_max_size)
        fh.setFormatter(_FileFormatter(file_formats))
        fh.setLevel(file_level.value if isinstance(file_level, _Levels) else file_level)
        fh.terminator = file_terminator
        LoggerBuilder.__finalize_setup(logger, fh, _logging.FileHandler, remove_handlers)

    @staticmethod
    def __finalize_setup(logger, new_handler, handler_type, remove_handlers):
        if remove_handlers:
            for handler in list(logger.handlers):
                if isinstance(handler, handler_type):
                    logger.handlers.remove(handler)
        logger.addHandler(new_handler)
