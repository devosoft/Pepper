# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
The Symbol Table module implements a class to track declarations and usages of identifiers
"""
import sys
import platform
import re  # because we need more performance issues

#: The global symboltable
TABLE = dict()  # Identifier/argment list length pairs.
#: The stack of files we're reading from
FILE_STACK = []
#: The stack of ifdef/ifndef/if control structures we're processing
IFDEF_STACK = []
#: The list of paths to search when doing a system include
SYSTEM_INCLUDE_PATHS = []
EXPANDED_MACRO = False
#: Switch to test internal error handling
TRIGGER_INTERNAL_ERROR = False

#: The default linux paths to search for includes-
LINUX_DEFAULTS = [
    "/usr/include/c++/7",
    "/usr/include/x86_64-linux-gnu/c++/7",
    "/usr/include/c++/7/backward",
    "/usr/lib/gcc/x86_64-linux-gnu/7/include",
    "/usr/local/include",
    "/usr/lib/gcc/x86_64-linux-gnu/7/include-fixed",
    "/usr/include/x86_64-linux-gnu",
    "/usr/include"
]

MAC_DEFAULTS = [
    "/usr/local/include",
    "/Library/Developer/CommandLineTools/usr/include/c++/v1",
    "/Library/Developer/CommandLineTools/usr/lib/clang/9.0.0/include",
    "/Library/Developer/CommandLineTools/usr/include",
    "/usr/include"

]

if platform.system() == "Linux":
    SYSTEM_INCLUDE_PATHS = LINUX_DEFAULTS

elif platform.system() == "Darwin":
    SYSTEM_INCLUDE_PATHS = MAC_DEFAULTS


class PepperSyntaxError(Exception):
    pass


class PepperInternalError(Exception):
    pass


class MacroExpansion():
    "Expands an identifier into a macro expansion, possibly with arguments"
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
        global EXPANDED_MACRO
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
        EXPANDED_MACRO = True

        if args:
            for index, arg in enumerate(args):
                expansion = re.sub(fr"\b{self.args[index]}\b", str(arg), expansion)
        return expansion

    def preprocess(self, lines):
        if TRIGGER_INTERNAL_ERROR:
            raise Exception
        lines[-1] += "// " + self.__str__()

    def __str__(self):
        return f"Macro {self.name} with args {self.args} expanding to '{self.expansion}'"
