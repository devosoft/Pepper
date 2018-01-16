"""
The Symbol Table module implements a class to track declarations and usages of identifiers
"""
import sys

TABLE = dict()  # Identifier/argment list length pairs.
FILE_QUEUE = []


class MacroExpansion():
    def __init__(self, name, expansion, args=None):
        self.name = name
        self.expansion = ""

        for item in expansion:
            self.expansion += item.preprocess()
        self.args = args

        if self.name in TABLE.keys():
            print(f"Warning: Redefining macro '{self.name}'", file=sys.stderr)

        TABLE[self.name] = self

    def expand(self, args=None):
        if self.args is None and args is not None:
            raise SyntaxError(f"Macro {self.name} doesn't take any args, but was given {len(args)}")
        elif self.args is not None and args is None:
            raise SyntaxError(f"Macro {self.name} takes {len(self.args)}, but was given none."
                              " (Did you forget parens?)")
        elif self.args is None and args is None:
            pass
        elif len(args) != len(self.args):
            raise SyntaxError(f"Wrong number of arguments in macro expansion for {self.name};"
                              f" expected {len(self.args)}, got {len(args)}")

        expansion = self.expansion

        if args:
            for index, arg in enumerate(args):
                expansion = expansion.replace(self.args[index], str(arg))
        return expansion

    def preprocess(self, lines):
        lines[-1] += "// " + self.__str__()

    def __str__(self):
        return f"Macro {self.name} with args {self.args} expanding to '{self.expansion}'"
