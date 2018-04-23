# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
The Symbol Table module implements a class to track declarations and usages of identifiers
"""
import sys
import re  # because we need more performance issues
import subprocess
from typing import (
    Dict,
    TextIO,
    List,
    Tuple,
    Any,
    Optional,
    Union,
    cast)

#: The stack of files we're reading from
FILE_STACK: List[TextIO] = []
#: The stack of ifdef/ifndef/if control structures we're processing
IF_STACK: List[Tuple[str, bool]] = []
#: The list of paths to search when doing a system include
SYSTEM_INCLUDE_PATHS: List[str] = []
EXPANDED_MACRO = False
#: Switch to test internal error handling
TRIGGER_INTERNAL_ERROR = False
#: Count of if directive calls
IF_COUNT = 0
#: Global Line Count
LINE_COUNT = 0
def build_default_include_lists() -> List[str]:
    p = subprocess.run(["cpp", "-v", "/dev/null", "-o", "/dev/null"],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    output_lines = p.stderr.decode('utf-8').split("\n")

    found_include_listing = False
    default_include = []
    for line in output_lines:
        line = line.strip()
        if found_include_listing:
            if line.startswith("End of search list."):
                found_include_listing = False
            else:
                default_include.append(line)
        elif line.startswith("#include <...> search starts here:"):
            found_include_listing = True

    return default_include


SYSTEM_INCLUDE_PATHS = build_default_include_lists()


class Node():
    def __init__(self, name: str, children: Union[List[str], List['Node']]) -> None:
        self.name = name
        self.children = children

    def __str__(self) -> str:
        lines = [f"Node: {self.name}"]

        for child in self.children:
            lines.append(f"\t{str(child)}")

        return "\n".join(lines)

    def preprocess(self, lines: Optional[List[str]] = None) -> str:
        raise NotImplementedError()


class PepperSyntaxError(Exception):
    def __init__(self, msg: str="") -> None:
        self.msg = msg


class PepperInternalError(Exception):
    def __init__(self, msg: str="") -> None:
        self.msg = msg

class MacroExpansion():
    "Expands an identifier into a macro expansion, possibly with arguments"
    def __init__(self, name: str, expansion: List[Node], args: Optional[List[str]] = None) -> None:
        self.name = name
        self.expansion = ""
        self.tokens: List[Node] = []
        self.args = args
        self.variadic = False

        if args is not None:
            for index, arg in enumerate(args):
                if arg.endswith("..."):
                    if index != len(args) - 1:
                        raise PepperSyntaxError("Variadic macro argument must be at the end of the"
                                                " argument definition list")
                    self.variadic = True

        for token in expansion:
                self.tokens.append(token)

        for item in expansion:
            preprocessed = item.preprocess()
            self.expansion += preprocessed if preprocessed is not None else ""
        if self.name in TABLE.keys():
            print(f"Warning: Redefining macro '{self.name}'", file=sys.stderr)

        TABLE[self.name] = self

    def _validate_args(self, args: Optional[List[str]]) -> None:
        "Internal arg validator, broken out since it was getting long"
        if self.variadic:
            if args is None:
                raise PepperSyntaxError(f"Macro {self.name} invoked without args, but is variadic")
            elif self.args is None:
                raise PepperInternalError(f"Impossible state, we're variadic but have no args")
            elif len(args) <= len(self.args) - 1:
                raise PepperSyntaxError(f"Macro {self.name} was given {len(args)} arguments,"
                                        f" but takes a minimum of {len(self.args) + 1}")
        else:
            if self.args is None and args is not None:
                raise PepperSyntaxError(f"Macro {self.name} doesn't take any args,"
                                        f" but was given {len(args)}")
            elif self.args is None and args is None:
                return
            elif self.args is not None and args is None:
                raise PepperSyntaxError(f"Macro {self.name} expects args, but was given none.")
            else:
                assert(self.args is not None and args is not None)
                if len(args) != len(self.args):  # typechecker isn't as clever as I want it to be
                    raise PepperSyntaxError(f"Wrong number of arguments in macro expansion for "
                                            f"{self.name}; expected {len(self.args)},"
                                            f" got {len(args)}")

    def expand(self, args: Any = None) -> str:
        "Expand macro, maybe with args"
        global EXPANDED_MACRO
        # try:
        self._validate_args(args)

        expansion = self.expansion[:]
        EXPANDED_MACRO = True

        if args:
            stripped_args: List[str] = [arg.strip() for arg in args]

            if self.variadic:
                # for some reason slicing this inline doesn't work
                assert(self.args is not None)
                non_variadic_args = stripped_args[:len(self.args)-1]
                variadic_args = stripped_args[len(non_variadic_args):]

                for index, arg in enumerate(non_variadic_args):
                    expansion = re.sub(fr"\b{self.args[index]}\b", str(arg), expansion)

                variadic_target = "__VA__ARGS__"

                if len(self.args[-1]) > 3:  # named variadic target, i.e. "args..."
                    variadic_target = self.args[-1][:-3]

                expansion = re.sub(fr"{variadic_target}", ", ".join(variadic_args), expansion)
            else:
                for index, arg in enumerate(stripped_args):
                    replacement = cast(List[str], self.args)[index]
                    expansion = re.sub(fr"\b{replacement}\b",
                                       str(arg),
                                       expansion)
        return expansion

    def preprocess(self, lines: List[str] = []) -> None:
        if TRIGGER_INTERNAL_ERROR:
            raise Exception
        lines[-1] += "// " + self.__str__()

    def __str__(self) -> str:
        return f"Macro {self.name} with args {self.args} expanding to '{self.expansion}'"


TABLE: Dict[str, MacroExpansion] = dict()
