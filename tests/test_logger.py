import re
import unittest
from io import StringIO
from unittest.mock import patch

from melogger import LoggerBuilder, Levels, FORMATS, Colors, FileFormatter, ConsoleFormatter


class LoggerTest(unittest.TestCase):
    ENABLE_OUTPUT_REDIRECT = True

    @classmethod
    def setUp(cls):
        mock_formatter = patch("melogger.builder._ConsoleFormatter").start()
        cls.console_mock = None
        cls.file_mock = None

        mock_formatter.side_effect = ConsoleFormatter
        if cls.ENABLE_OUTPUT_REDIRECT:
            cls.console_mock = patch("melogger.builder._sys").start() if cls.ENABLE_OUTPUT_REDIRECT else None
            cls.console_mock.stdout = StringIO()
            cls.console_output = cls.console_mock.stdout
        cls.logger = LoggerBuilder.build("ConsoleLogger", level=Levels.DEBUG)

        mock_formatter.side_effect = FileFormatter
        if cls.ENABLE_OUTPUT_REDIRECT:
            cls.file_mock = patch("melogger.builder._sys").start()
            cls.file_mock.stdout = StringIO()
            cls.file_output = cls.file_mock.stdout
        cls.logger_file = LoggerBuilder.build("FileLogger", level=Levels.DEBUG)

    @classmethod
    def __get_console_output(cls):
        if cls.ENABLE_OUTPUT_REDIRECT:
            cls.console_output.seek(0)
            return cls.console_mock.stdout.readlines()
        return []

    @classmethod
    def __get_file_output(cls):
        if cls.ENABLE_OUTPUT_REDIRECT:
            cls.file_output.seek(0)
            return cls.file_mock.stdout.readlines()
        return []

    @classmethod
    def __get_parsed_string(cls, level, message, full_line, colored, pref=None, suffix=None):
        level_data = FORMATS.get(level.value if isinstance(level, Levels) else level)
        output = level_data.text_format.replace("%(pref)s", ("^" if full_line else "") + (pref if pref else ""))
        output = output.replace("%(col_start)s", r"\033\[[\d;]*[A-Za-z]" if colored else "")
        output = output.replace("%(asctime)s", r"\d{4}-\d{2}-\d{2} (\d{2}:?){3},\d{3}")
        output = output.replace("[%(level_name)s]", rf"\[{level_data.label}]")
        output = output.replace("%(module)s", r"\w+")
        output = output.replace("(%(process)d)", r"\(\w+\)")
        output = output.replace("%(message)s", message)
        output = output.replace("%(col_end)s", r"\033\[[\d;]*[A-Za-z]" if colored else "")
        output = output.replace("%(terminator)s", (suffix if suffix else "") + ("$" if full_line else ""))
        return output

    @classmethod
    def __get_level_regex(cls, level, message, full_line, colored, pref=None, suffix=None):
        return re.compile(cls.__get_parsed_string(level, message, full_line, colored, pref, suffix))

    @classmethod
    def __get_combined_regex(cls, *args):
        return re.compile(''.join(args))

    def test_change_level(self):
        self.logger.debug("Message debug 1")
        self.logger.debug("Message debug 2", color=Colors.COL.YELLOW)
        self.logger.setLevel(Levels.INFO)
        self.logger.debug("Message debug 3")
        self.logger.debug("Message debug 4")

        lines = self.__get_console_output()
        self.assertTrue(len(lines) == 3)

    def test_logger_methods(self):
        self.logger.debug("Message debug")
        self.logger.info("Message info")
        self.logger.info("Message info color", color=Colors.COL.MAGENTA)
        self.logger.warning("Message warning")
        self.logger.error("Message error")
        self.logger.critical("Message critical")
        self.logger.plain("Message plain")

        lines = self.__get_console_output()
        self.assertRegex(lines[1], self.__get_level_regex(Levels.DEBUG.value, "Message debug", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.INFO.value, "Message info", full_line=True, colored=True))
        self.assertRegex(lines[3], self.__get_level_regex(Levels.INFO.value, "Message info color", full_line=True, colored=True))
        self.assertRegex(lines[4], self.__get_level_regex(Levels.WARN.value, "Message warning", full_line=True, colored=True))
        self.assertRegex(lines[5], self.__get_level_regex(Levels.ERROR.value, "Message error", full_line=True, colored=True))
        self.assertRegex(lines[6], self.__get_level_regex(Levels.CRITICAL.value, "Message critical", full_line=True, colored=True))
        self.assertRegex(lines[7], self.__get_level_regex(Levels.PLAIN.value, "Message plain", full_line=True, colored=True))

    def test_remove_color_inside_files(self):
        self.logger_file.debug("Message debug - file")
        self.logger_file.info("Message info - file")
        self.logger_file.info("Message info color - file", color=Colors.COL.MAGENTA)
        self.logger_file.warning("Message warning - file")
        self.logger_file.error("Message error - file")
        self.logger_file.critical("Message critical - file")
        self.logger_file.plain("Message plain - file")

        lines = self.__get_file_output()
        self.assertRegex(lines[1], self.__get_level_regex(Levels.DEBUG.value, "Message debug - file", full_line=True, colored=False))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.INFO.value, "Message info - file", full_line=True, colored=False))
        self.assertRegex(lines[3], self.__get_level_regex(Levels.INFO.value, "Message info color - file", full_line=True, colored=False))
        self.assertRegex(lines[4], self.__get_level_regex(Levels.WARN.value, "Message warning - file", full_line=True, colored=False))
        self.assertRegex(lines[5], self.__get_level_regex(Levels.ERROR.value, "Message error - file", full_line=True, colored=False))
        self.assertRegex(lines[6], self.__get_level_regex(Levels.CRITICAL.value, "Message critical - file", full_line=True, colored=False))
        self.assertRegex(lines[7], self.__get_level_regex(Levels.PLAIN.value, "Message plain - file", full_line=True, colored=False))

    def test_pref_handling_01(self):
        # Non Plain: blank | Plain: \r
        self.logger.info("Message 1", end='')
        self.logger.plain("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.INFO.value, "Message 1", full_line=False, colored=True, pref='^'), '\r',
            self.__get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.info("Message 1", end='')
        self.logger_file.plain("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_02(self):
        # Non Plain: blank | Non-Plain: \r
        self.logger.info("Message 1", end='')
        self.logger.info("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.INFO.value, "Message 1", full_line=False, colored=True, pref="^"), '\r',
            self.__get_parsed_string(Levels.INFO.value, "Message 2", full_line=False, colored=True, suffix="$"),
        ))

        self.logger_file.info("Message 1", end='')
        self.logger_file.info("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_03(self):
        # Non Plain: blank | Plain: \t
        self.logger.info("Message 1", end='')
        self.logger.plain("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.INFO.value, "Message 1", full_line=False, colored=True, pref="^"), '\t',
            self.__get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.info("Message 1", end='')
        self.logger_file.plain("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.INFO.value, "Message 1", full_line=False, colored=False, pref="^"), '\t',
            self.__get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=False, suffix="$")
        ))

    def test_pref_handling_04(self):
        # Non Plain: blank | Non-Plain: \t
        self.logger.info("Message 1", end='')
        self.logger.info("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.INFO.value, "Message 1", full_line=False, colored=True, pref="^"), '\t',
            self.__get_parsed_string(Levels.INFO.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.info("Message 1", end='')
        self.logger_file.info("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False, pref='\t'))

    def test_pref_handling_05(self):
        # Non Plain: \n   | Plain: \r
        self.logger.info("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=True, pref='\r'))

        self.logger_file.info("Message 1", end='\n')
        self.logger_file.plain("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_06(self):
        # Non Plain: \n   | Non-Plain: \r
        self.logger.info("Message 1", end='\n')
        self.logger.info("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=True, pref='\r'))

        self.logger_file.info("Message 1", end='\n')
        self.logger_file.info("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_07(self):
        # Non Plain: \n   | Plain: \t
        self.logger.info("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=True, pref='\t'))

        self.logger_file.info("Message 1", end='\n')
        self.logger_file.plain("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=False, pref='\t'))

    def test_pref_handling_08(self):
        # Non Plain: \n   | Non-Plain: \t
        self.logger.info("Message 1", end='\n')
        self.logger.info("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=True, pref='\t'))

        self.logger_file.info("Message 1", end='\n')
        self.logger_file.info("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False, pref='\t'))

    def test_pref_handling_09(self):
        # Plain: blank    | Plain: \r
        self.logger.plain("Message 1", end='')
        self.logger.plain("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.PLAIN.value, "Message 1", full_line=False, colored=True, pref="^"), '\r',
            self.__get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.plain("Message 1", end='')
        self.logger_file.plain("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_10(self):
        # Plain: blank    | Non-Plain: \r
        self.logger.plain("Message 1", end='')
        self.logger.info("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.PLAIN.value, "Message 1", full_line=False, colored=True, pref="^"), '\r',
            self.__get_parsed_string(Levels.INFO.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.plain("Message 1", end='')
        self.logger_file.info("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_11(self):
        # Plain: blank    | Plain: \t
        self.logger.plain("Message 1", end='')
        self.logger.plain("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.PLAIN.value, "Message 1", full_line=False, colored=True, pref="^"), '\t',
            self.__get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.plain("Message 1", end='')
        self.logger_file.plain("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.PLAIN.value, "Message 1", full_line=False, colored=False, pref="^"), '\t',
            self.__get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=False, suffix="$"),

        ))

    def test_pref_handling_12(self):
        # Plain: blank    | Non-Plain: \t
        self.logger.plain("Message 1", end='')
        self.logger.info("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(2, len(lines))
        self.assertRegex(lines[1], self.__get_combined_regex(
            self.__get_parsed_string(Levels.PLAIN.value, "Message 1", full_line=False, colored=True, pref="^"), '\t',
            self.__get_parsed_string(Levels.INFO.value, "Message 2", full_line=False, colored=True, suffix="$")
        ))

        self.logger_file.plain("Message 1", end='')
        self.logger_file.info("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False, pref="\t"))

    def test_pref_handling_13(self):
        # Plain: \n       | Plain: \r
        self.logger.plain("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=True, pref="\r"))

        self.logger_file.plain("Message 1", end='\n')
        self.logger_file.plain("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_14(self):
        # Plain: \n       | Non-Plain: \r
        self.logger.plain("Message 1", end='\n')
        self.logger.info("Message 2", pref='\r')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=True, pref="\r"))

        self.logger_file.plain("Message 1", end='\n')
        self.logger_file.info("Message 2", pref='\r')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=False))

    def test_pref_handling_15(self):
        # Plain: \n       | Plain: \t
        self.logger.plain("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=True, pref="\t"))

        self.logger_file.plain("Message 1", end='\n')
        self.logger_file.plain("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=False, pref="\t"))

    def test_pref_handling_16(self):
        # Plain: \n       | Non-Plain: \t
        self.logger.plain("Message 1", end='\n')
        self.logger.info("Message 2", pref='\t')
        lines = self.__get_console_output()
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=True))
        self.assertRegex(lines[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=True, pref="\t"))

        self.logger_file.plain("Message 1", end='\n')
        self.logger_file.info("Message 2", pref='\t')
        lines_file = self.__get_file_output()
        self.assertEqual(3, len(lines_file))
        self.assertRegex(lines_file[1], self.__get_level_regex(Levels.PLAIN.value, "Message 1", full_line=False, colored=False))
        self.assertRegex(lines_file[2], self.__get_level_regex(Levels.INFO.value, "Message 2", full_line=False, colored=False, pref="\t"))
