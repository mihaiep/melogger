import os
import time
import unittest
from unittest.mock import patch

from melogger import LoggerBuilder, Levels, Colors


class LoggerTest(unittest.TestCase):
    ESCAPED_MODIFIER = r'\033\[[\d;]*[A-Za-z]'
    LOG_FORMAT = r'^\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d \[{}] \w+ \(\d+\) {}$'
    LOG_FORMAT_COLORED = ESCAPED_MODIFIER + r'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d \[{}] \w+ \(\d+\)' + ESCAPED_MODIFIER + ' {}'

    @classmethod
    def tearDownClass(cls):
        os.remove('test.log')

    def test_logger(self) -> None:
        logger = LoggerBuilder.get_logger("test", level=Levels.DEBUG, file_name="test.log", file_mode='w')
        logger.debug("message debug test")
        logger.info("message info test")
        logger.warning("message warning test")
        logger.error("message error test")
        logger.critical("message critical test")
        logger.plain("message plain")

        del logger
        with open('test.log', 'r') as f:
            lines = f.read().splitlines()

        self.assertTrue("DEBUG" in lines[1] and "message debug test" in lines[1])
        self.assertTrue("INFO" in lines[2] and "message info test" in lines[2])
        self.assertTrue("WARN" in lines[3] and "message warning test" in lines[3])
        self.assertTrue("ERROR" in lines[4] and "message error test" in lines[4])
        self.assertTrue("CRITICAL" in lines[5] and "message critical test" in lines[5])
        self.assertTrue("message plain" in lines[6])

    def test_color_removal(self) -> None:
        logger = LoggerBuilder.get_logger("test", level=Levels.DEBUG, file_name="test.log", file_mode='w')
        logger.debug("debug message")
        logger.info("info message")
        logger.info_green("info green message")
        logger.info_color("info color message1", color=Colors.COL.RED)
        logger.info_color("info color message2", color=Colors.rgb(160, 50, 37))
        logger.info_color("info color message3", color=Colors.hex("#AB05A1"))
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")

        logger.plain("Yellow text", color=Colors.COL.YELLOW)
        logger.plain("Color red.", color=Colors.COL.RED)
        logger.plain("Color yellow {}inside{} string".format(Colors.COL.YELLOW, Colors.END))
        logger.plain(f"{Colors.rgb(255, 255, 255)}{Colors.BGD.BLACK}A new highlighted with message{Colors.END}")

        del logger
        with open('test.log', 'r') as f:
            lines = f.read().splitlines()

        self.assertRegex(lines[1], LoggerTest.LOG_FORMAT.format("DEBUG", "debug message"))
        self.assertRegex(lines[2], LoggerTest.LOG_FORMAT.format("INFO", "info message"))
        self.assertRegex(lines[3], LoggerTest.LOG_FORMAT.format("INFO", "info green message"))
        self.assertRegex(lines[4], LoggerTest.LOG_FORMAT.format("INFO", "info color message1"))
        self.assertRegex(lines[5], LoggerTest.LOG_FORMAT.format("INFO", "info color message2"))
        self.assertRegex(lines[6], LoggerTest.LOG_FORMAT.format("INFO", "info color message3"))
        self.assertRegex(lines[7], LoggerTest.LOG_FORMAT.format("WARN", "warning message"))
        self.assertRegex(lines[8], LoggerTest.LOG_FORMAT.format("ERROR", "error message"))
        self.assertRegex(lines[9], LoggerTest.LOG_FORMAT.format("CRITICAL", "critical message"))
        self.assertRegex(lines[10], "^Yellow text$")
        self.assertRegex(lines[11], "^Color red.$")
        self.assertRegex(lines[12], "^Color yellow inside string$")
        self.assertRegex(lines[13], "^A new highlighted with message$")

    def test_cr_removal(self) -> None:
        logger = LoggerBuilder.get_logger("test", level=Levels.DEBUG, file_name="test.log", file_mode='w')
        logger.debug("This is a test", extra={'end': ""})
        time.sleep(0.25)
        logger.info("This should be written over 1st line just in console", extra={'col_start': f"{Colors.COL.BLUE}", 'start': "\r", "end": ""})
        time.sleep(0.25)
        logger.warning("This should be fourth line in log file", extra={'col_start': f"{Colors.COL.RED}", 'start': "\r", "end": ""})
        time.sleep(0.25)
        logger.error("This should be fifth line in log file", extra={'col_start': f"{Colors.COL.RED}", 'start': "\r", "end": ""})
        time.sleep(0.25)
        logger.critical("This should be sixth line in log file", extra={'col_start': f"{Colors.COL.RED}", 'start': "\r", "end": ""})
        time.sleep(0.25)

        del logger
        with open('test.log', 'r') as f:
            lines = f.read().splitlines()

        self.assertRegex(lines[1], LoggerTest.LOG_FORMAT.format("DEBUG", "This is a test"))
        self.assertRegex(lines[2], LoggerTest.LOG_FORMAT.format("INFO", "This should be written over 1st line just in console"))
        self.assertRegex(lines[3], LoggerTest.LOG_FORMAT.format("WARN", "This should be fourth line in log file"))
        self.assertRegex(lines[4], LoggerTest.LOG_FORMAT.format("ERROR", "This should be fifth line in log file"))
        self.assertRegex(lines[5], LoggerTest.LOG_FORMAT.format("CRITICAL", "This should be sixth line in log file"))

    def test_cr_removal2(self) -> None:
        from io import StringIO
        mock = patch("melogger.builder._sys").start()
        mock.stdout = StringIO()
        tmp_out = mock.stdout
        output = ["{",
                  '\t"ip": "200.200.200.200",',
                  '\t"port": "8080"',
                  '}']

        logger = LoggerBuilder.get_logger("test", level=Levels.DEBUG, file_name="test.log", file_mode='w')

        logger.info("Getting: https://localhost", extra={"end": ""})
        logger.info("Getting: https://localhost - sleep 60", extra={"start": "\r", "end": ""})
        logger.info("Getting: https://localhost - sleep 60", extra={"start": "\r", "end": ""})
        logger.info("Getting: https://localhost - sleep 60", extra={"start": "\r", "end": ""})
        tmp_out.seek(0)
        last = mock.stdout.readlines()[-1]
        self.assertRegex(last, LoggerTest.LOG_FORMAT_COLORED.format("INFO", "Getting: https://localhost") +
                         "(\r" + LoggerTest.LOG_FORMAT_COLORED.format("INFO", "Getting: https://localhost - sleep 60") + "){3}")

        logger.error("Too manny retries - Sleep 600s", extra={'start': '\n'})
        tmp_out.seek(0)
        last = mock.stdout.readlines()[-1]
        self.assertRegex(last, LoggerTest.LOG_FORMAT_COLORED.format("ERROR", "Too manny retries - Sleep 600s"))

        logger.info("Getting: https://localhost", extra={"end": ""})
        tmp_out.seek(0)
        last = mock.stdout.readlines()[-1]
        self.assertRegex(last, LoggerTest.LOG_FORMAT_COLORED.format("INFO", "Getting: https://localhost"))

        logger.info("Processing", extra={"start": '\r'})
        tmp_out.seek(0)
        last = mock.stdout.readlines()[-1]
        self.assertRegex(last, LoggerTest.LOG_FORMAT_COLORED.format("INFO", "Getting: https://localhost") + "\r" + LoggerTest.LOG_FORMAT_COLORED.format("INFO", "Processing"))

        logger.plain('\n'.join(output))
        tmp_out.seek(0)
        last = "".join(mock.stdout.readlines()[-4:])
        self.assertRegex(last, self.ESCAPED_MODIFIER + '\n'.join(output) + self.ESCAPED_MODIFIER)
