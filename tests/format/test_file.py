import unittest
from unittest.mock import MagicMock

from melogger import FORMATS, FileFormatter, Colors


class FileFormatterTest(unittest.TestCase):

    def setUp(self):
        self.message = MagicMock()

    def test_custom_format(self):
        formatter = FileFormatter(FORMATS)
        formatter._FileFormatter__handle_pref = lambda x: x

        self.message.col_start = "test"
        self.message.col_end = "test"
        self.message.msg = f"This {Colors.COL.GREEN}is a message with{Colors.BGD.GREEN} colors{Colors.END}"
        formatter.custom_format(self.message)

        self.assertEqual("", self.message.col_start)
        self.assertEqual("", self.message.col_end)
        self.assertEqual("This is a message with colors", self.message.msg)
