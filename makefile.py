import re
import itertools

class Makefile:
    class LineTypes:
        TargetStart = 1
        TargetEnd = 2
        PruningFile = 3

    class Strings:
        TARGET_START = r"Considering target file '(.*)'\."
        TARGET_END = r"Finished prerequisites of target file '(.*)'\."
        PRUNING_FILE = r"Pruning file '(.*)'\."

        @staticmethod
        def level(line):
            return sum([1 for _ in itertools.takewhile(str.isspace, line)])

        @classmethod
        def target(cls, line):
            search = re.search(cls.TARGET_START, line)

            if search:
                return search.group(1), Makefile.LineTypes.TargetStart

            search = re.search(cls.TARGET_END, line)

            if search:
                return search.group(1), Makefile.LineTypes.TargetEnd

            search = re.search(cls.PRUNING_FILE, line)

            if search:
                return search.group(1), Makefile.LineTypes.PruningFile

            return None, None
