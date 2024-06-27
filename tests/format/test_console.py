import unittest
from unittest.mock import MagicMock

from melogger import FORMATS, Levels, Colors, ConsoleFormatter


class ConsoleFormatterTest(unittest.TestCase):

    def setUp(self):
        self.message = MagicMock()

    def test_validate_pref(self):
        for val in [1, "<", '\n', "\r\n", "\t\n"]:
            self.message.prefix = val
            # noinspection PyUnresolvedReferences
            self.assertRaises(Exception, ConsoleFormatter._ConsoleFormatter__validate_pref, self.message)

        try:
            for val in ['', ' ', '\t', '\r', '\r\r', '\t \r']:
                self.message.prefix = val
                # noinspection PyUnresolvedReferences
                ConsoleFormatter._ConsoleFormatter__validate_pref(self.message)
        except ValueError:
            self.fail("Should not have raised exception")

    def test_validate_terminator(self):
        for val in [1, " ", "<", '\r', "\r\n", "\t\n"]:
            self.message.terminator = val
            # noinspection PyUnresolvedReferences
            self.assertRaises(Exception, ConsoleFormatter._ConsoleFormatter__validate_terminator, self.message)

        try:
            for val in ['', '\n\n']:
                self.message.terminator = val
                # noinspection PyUnresolvedReferences
                ConsoleFormatter._ConsoleFormatter__validate_terminator(self.message)
        except ValueError:
            self.fail("Should not have raised exception")

    def test_custom_format(self):
        formatter = ConsoleFormatter(FORMATS)
        formatter.level_data = FORMATS.get(Levels.WARN.value)

        self.message.col_start = f" \t{Colors.COL.BLACK} \t"

        formatter.custom_format(self.message)
        self.assertEqual(Colors.END, self.message.col_end)
        self.assertEqual(Colors.COL.BLACK, self.message.col_start)

        del self.message.col_start, self.message.col_end
        formatter.custom_format(self.message)
        self.assertEqual(Colors.END, self.message.col_end)
        self.assertEqual(Colors.COL.YELLOW, self.message.col_start)
