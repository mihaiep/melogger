import re

from melogger import FORMATS, Levels


class FormatterExtension:
    output = None
    output_mock = None
    logger = None
    colored = False

    @classmethod
    def __print_output(cls, data, label):
        print('\r{delim}\n > {label}\n{delim}\n{data}\n{delim}'.format(delim='-' * 100, label=label, data=data))

    @classmethod
    def _get_output(cls):
        cls.output.seek(0)
        output = cls.output.readlines()
        cls.__print_output(''.join(output), "Console Output")
        return output

    @classmethod
    def _get_parsed_string(cls, level, message, full_line, colored, prefix=None, suffix=None):
        level_data = FORMATS.get(level.value if isinstance(level, Levels) else level)
        output = level_data.text_format.replace("%(prefix)s", ("^" if full_line else "") + (prefix if prefix else ""))
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
    def _get_level_regex(cls, level, message, full_line, colored, prefix=None, suffix=None):
        return re.compile(cls._get_parsed_string(level, message, full_line, colored, prefix, suffix))

    @classmethod
    def _get_combined_regex(cls, *args):
        return re.compile(''.join(args))


