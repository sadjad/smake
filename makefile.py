import re
import itertools

class Makefile:
    class Line:
    class Strings:
        TARGET_START = r"Considering target file '(.*)'\."
        TARGET_END = r"Finished prerequisites of target file '(.*)'\."

        @staticmethod
        def level(line):
            return sum([1 for _ in itertools.takewhile(str.isspace, line)])

        @classmethod
        def target(cls, line):
            search = re.search(cls.TARGET_START, line)

            if search:
                return search.group(1)

            return None
