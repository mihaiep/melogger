import os
import unittest

from melogger import LoggerBuilder, Levels, Colors
from melogger.utils import LevelData


class LoggerTest(unittest.TestCase):
    ESCAPED_MODIFIER = r'\033\[[\d;]*[A-Za-z]'
    LOG1_FORMAT = r'^<{}> \(\d+\) {}$'
    LOG2_FORMAT = r'^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d \[{}] \w+ \(\d+\) {}$'

    @classmethod
    def tearDownClass(cls):
        os.remove('test1.log')
        os.remove('test2.log')

    def test_build_logger(self):
        FORMATS = {
            Levels.DEBUG.value: LevelData("DEBUG", Colors.COL.GREY, "<%(levelname)s> (%(process)d) %(message)s%(terminator)s"),
            Levels.INFO.value: LevelData("INFO", Colors.COL.DEFAULT, "<%(levelname)s> (%(process)d) %(message)s%(terminator)s"),
            Levels.WARN.value: LevelData("WARN", Colors.COL.YELLOW, "<%(levelname)s> (%(process)d) %(message)s%(terminator)s"),
            Levels.ERROR.value: LevelData("ERROR", Colors.COL.RED, "<%(levelname)s> (%(process)d) %(message)s%(terminator)s"),
            Levels.CRITICAL.value: LevelData("CRITICAL", Colors.COL.PURE.RED, "<%(levelname)s> (%(process)d) %(message)s%(terminator)s"),
            Levels.PLAIN.value: LevelData("PLAIN", Colors.COL.DEFAULT, "%(start)s%(col_start)s%(message)s%(terminator)s")
        }

        logger1 = LoggerBuilder.get_logger("test1", level=Levels.DEBUG, formats=FORMATS, file_name="test1.log", file_mode='w')
        logger2 = LoggerBuilder.get_logger("test2", level=Levels.DEBUG, file_name="test2.log", file_mode='w')
        self.assertEqual(logger1.name, 'test1')
        self.assertEqual(logger2.name, 'test2')

        logger1.warning("message info test1")
        logger2.warning("message info test2")

        del logger1, logger2
        with open('test1.log', 'r') as f: lines1 = f.read().splitlines()
        with open('test2.log', 'r') as f: lines2 = f.read().splitlines()

        self.assertRegex(lines1[0], LoggerTest.LOG1_FORMAT.format('INFO', 'Execution started'))
        self.assertRegex(lines1[1], LoggerTest.LOG1_FORMAT.format('WARN', 'message info test1'))
        self.assertRegex(lines2[0], LoggerTest.LOG2_FORMAT.format('INFO', 'Execution started'))
        self.assertRegex(lines2[1], LoggerTest.LOG2_FORMAT.format('WARN', 'message info test2'))
