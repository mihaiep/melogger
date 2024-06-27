import os.path
import unittest
from types import MappingProxyType

from melogger import LoggerBuilder, Levels, Colors
from melogger.utils import LevelData


class LoggerTest(unittest.TestCase):
    FORMATS = MappingProxyType({
        Levels.DEBUG.value: LevelData("DEBUG", Colors.COL.DEFAULT, "[--TEST--] [%(level_name)s] %(message)s%(terminator)s"),
        Levels.INFO.value: LevelData("INFO", Colors.COL.DEFAULT, "[--TEST--] [%(level_name)s] %(message)s%(terminator)s"),
        Levels.WARN.value: LevelData("WARN", Colors.COL.DEFAULT, "[--TEST--] [%(level_name)s] %(message)s%(terminator)s"),
        Levels.ERROR.value: LevelData("ERROR", Colors.COL.DEFAULT, "[--TEST--] [%(level_name)s] %(message)s%(terminator)s"),
        Levels.CRITICAL.value: LevelData("CRITICAL", Colors.COL.DEFAULT, "[--TEST--] [%(level_name)s] %(message)s%(terminator)s"),
        Levels.PLAIN.value: LevelData("PLAIN", Colors.COL.DEFAULT, "[--TEST--] [%(level_name)s] %(message)s%(terminator)s"),
    })

    @classmethod
    def setUpClass(cls):
        cls.logger = LoggerBuilder.build(
            name="LoggerME",
            logs_level=Levels.INFO,
            formats=LoggerTest.FORMATS,
            terminator="",
            logs_path="tmp",
            file_name='test_builder.log',
            file_terminator="",
            file_mode="a",
            file_enc="utf-8",
            file_backups=5,
            file_max_size=1024 * 100
        )

    @classmethod
    def tearDownClass(cls):
        for file in os.listdir("tmp"):
            os.remove(os.path.join("tmp", file))
        os.removedirs('tmp')

    def test_default_logger(self):
        self.assertEqual("LoggerME", self.logger.name)

        self.assertEqual(Levels.INFO.value, self.logger.level)

        for handler in [self.logger.handlers[0], self.logger.handlers[1]]:
            self.assertEqual(Levels.INFO.value, handler.level)
            self.assertEqual(LoggerTest.FORMATS, handler.formatter.FORMATS)
            self.assertEqual("", handler.terminator)

        self.assertEqual('a', self.logger.handlers[1].mode)
        self.assertEqual('utf-8', self.logger.handlers[1].encoding)
        self.assertEqual(5, self.logger.handlers[1].backupCount)
        self.assertEqual(102400, self.logger.handlers[1].maxBytes)

        self.assertTrue(os.path.isfile("tmp/test_builder.log"))

    def test_file_rotating_handler(self):
        line = "a" * 1000
        self.logger.handlers.pop(0)
        for i in range(200):
            self.logger.info(line)
        self.assertTrue(len(os.listdir("tmp")) == 2)
