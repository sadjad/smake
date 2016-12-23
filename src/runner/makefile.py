import re
import itertools

class Makefile:
    class Lines:
        TargetStart = 1
        TargetEnd = 2
        PruningFile = 3
        MustRemake = 4
        RemakeDone = 5

        TARGET_START = (r"Considering target file '(.*)'\.", TargetStart)
        TARGET_END = (r"Finished prerequisites of target file '(.*)'\.", TargetEnd)
        PRUNING_FILE = (r"Pruning file '(.*)'\.", PruningFile)
        MUST_REMAKE = (r"Must remake target '(.*)'\.", MustRemake)
        REMAKE_DONE = (r"Successfully remade target file '(.*)'\.", RemakeDone)

        All = (
            TARGET_START, TARGET_END, PRUNING_FILE, MUST_REMAKE, REMAKE_DONE,
        )

    @staticmethod
    def level(line):
        return sum([1 for _ in itertools.takewhile(str.isspace, line)])

    @classmethod
    def identify(cls, line):
        for pattern, line_type in Makefile.Lines.All:
            search = re.search(pattern, line)

            if search:
                return search.group(1), line_type

        return None, None
