import unittest
from io import StringIO
from unittest.mock import patch

from melogger import LoggerBuilder, Levels, Logger, Colors
from tests.utils import FormatterExtension


class RotatingFileHandlerWithFileFormatterTest(unittest.TestCase, FormatterExtension):

    @classmethod
    def setUpClass(cls):
        print("\nLogger test - RotatingFileHandler - FileFormatterTest - no rollover ")

    @classmethod
    def setUp(cls):
        cls.output_mock = patch("builtins.open").start()
        cls.output = StringIO()
        cls.output_mock.return_value = cls.output
        cls.logger = Logger("FileLogger")
        cls.logger.addHandler(LoggerBuilder.get_file_handler("dummy.txt", Levels.DEBUG, file_max_size=0))
        cls.logger.setLevel(Levels.DEBUG)

    def test_remove_color_inside_files(self):
        self.logger.debug("Message debug")
        self.logger.info("Message info")
        self.logger.info("Message info color", color=Colors.COL.MAGENTA)
        self.logger.warning("Message warning")
        self.logger.error("Message error")
        self.logger.critical("Message critical")
        self.logger.plain("Message plain")

        lines = self._get_output()
        self.assertTrue(len(lines) == 7)
        self.assertRegex(lines[0], self._get_level_regex(Levels.DEBUG.value, "Message debug", full_line=True, colored=self.colored))
        self.assertRegex(lines[1], self._get_level_regex(Levels.INFO.value, "Message info", full_line=True, colored=self.colored))
        self.assertRegex(lines[2], self._get_level_regex(Levels.INFO.value, "Message info color", full_line=True, colored=self.colored))
        self.assertRegex(lines[3], self._get_level_regex(Levels.WARN.value, "Message warning", full_line=True, colored=self.colored))
        self.assertRegex(lines[4], self._get_level_regex(Levels.ERROR.value, "Message error", full_line=True, colored=self.colored))
        self.assertRegex(lines[5], self._get_level_regex(Levels.CRITICAL.value, "Message critical", full_line=True, colored=self.colored))
        self.assertRegex(lines[6], self._get_level_regex(Levels.PLAIN.value, "Message plain", full_line=True, colored=self.colored))

    def test_pref_handling_01(self):
        # Non Plain: blank | Plain: \r
        self.logger.info("Message 1", end='')
        self.logger.plain("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_02(self):
        # Non Plain: blank | Non-Plain: \r
        self.logger.info("Message 1", end='')
        self.logger.info("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_03(self):
        # Non Plain: blank | Plain: \t
        self.logger.info("Message 1", end='')
        self.logger.plain("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(1, len(lines_file))
        self.assertRegex(lines_file[0], self._get_combined_regex(
            self._get_parsed_string(Levels.INFO.value, "Message 1", full_line=False, colored=self.colored, pref="^"), '\t',
            self._get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=self.colored, suffix="$")
        ))

    def test_pref_handling_04(self):
        # Non Plain: blank | Non-Plain: \t
        self.logger.info("Message 1", end='')
        self.logger.info("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored, pref='\t'))

    def test_pref_handling_05(self):
        # Non Plain: \n   | Plain: \r
        self.logger.info("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_06(self):
        # Non Plain: \n   | Non-Plain: \r
        self.logger.info("Message 1", end='\n')
        self.logger.info("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_07(self):
        # Non Plain: \n   | Plain: \t
        self.logger.info("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=self.colored, pref='\t'))

    def test_pref_handling_08(self):
        # Non Plain: \n   | Non-Plain: \t
        self.logger.info("Message 1", end='\n')
        self.logger.info("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.INFO.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored, pref='\t'))

    def test_pref_handling_09(self):
        # Plain: blank    | Plain: \r
        self.logger.plain("Message 1", end='')
        self.logger.plain("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_10(self):
        # Plain: blank    | Non-Plain: \r
        self.logger.plain("Message 1", end='')
        self.logger.info("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_11(self):
        # Plain: blank    | Plain: \t
        self.logger.plain("Message 1", end='')
        self.logger.plain("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(1, len(lines_file))
        self.assertRegex(lines_file[0], self._get_combined_regex(
            self._get_parsed_string(Levels.PLAIN.value, "Message 1", full_line=False, colored=self.colored, pref="^"), '\t',
            self._get_parsed_string(Levels.PLAIN.value, "Message 2", full_line=False, colored=self.colored, suffix="$")
        ))

    def test_pref_handling_12(self):
        # Plain: blank    | Non-Plain: \t
        self.logger.plain("Message 1", end='')
        self.logger.info("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored, pref="\t"))

    def test_pref_handling_13(self):
        # Plain: \n       | Plain: \r
        self.logger.plain("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_14(self):
        # Plain: \n       | Non-Plain: \r
        self.logger.plain("Message 1", end='\n')
        self.logger.info("Message 2", pref='\r')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=True, colored=self.colored))

    def test_pref_handling_15(self):
        # Plain: \n       | Plain: \t
        self.logger.plain("Message 1", end='\n')
        self.logger.plain("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=True, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.PLAIN.value, "Message 2", full_line=True, colored=self.colored, pref="\t"))

    def test_pref_handling_16(self):
        # Plain: \n       | Non-Plain: \t
        self.logger.plain("Message 1", end='\n')
        self.logger.info("Message 2", pref='\t')
        lines_file = self._get_output()
        self.assertEqual(2, len(lines_file))
        self.assertRegex(lines_file[0], self._get_level_regex(Levels.PLAIN.value, "Message 1", full_line=False, colored=self.colored))
        self.assertRegex(lines_file[1], self._get_level_regex(Levels.INFO.value, "Message 2", full_line=False, colored=self.colored, pref="\t"))
