# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This is the abstract symbol tree for PEPPr.

The parser will build the actual tree, so this is really more of a library of nodes that may
be used within the tree.
"""
import pepper.symbol_table as symtable
from pepper.symbol_table import Node
import os
from typing import List, Any, Optional

from pathlib import Path


class LinesNode(Node):

    def __init__(self, children: List[Node] = []) -> None:
        children = [child for child in children if child is not None]
        super(LinesNode, self).__init__("Statements", children)

    def preprocess(self, lines: Optional[List[str]] = None) -> str:
        result = ""
        if lines:
            for child in self.children:
                child.preprocess(lines)
        else:
            result = "".join([r.preprocess() for r in self.children])
        return result


class PreprocessorDirectiveNode(Node):

    def __init__(self, children: List[Node] = []) -> None:
        super(PreprocessorDirectiveNode, self).__init__("PreprocessorDirective", children)


class PreprocessorIncludeNode(Node):

    def __init__(self, children: List[Any] = [], system_include: bool = False) -> None:
        super(PreprocessorIncludeNode, self).__init__("PreprocessorInclude", children)
        self.system_include = system_include
        self.target: str = children[0][1:-1]

    def __str__(self) -> str:
        return f"{self.name}: {self.children[0]}"

    @staticmethod
    def search_system_includes(filename: str) -> Path:
        for system_path in symtable.SYSTEM_INCLUDE_PATHS:
            candidate = Path(f"{system_path}/{filename}")
            if candidate.exists() and candidate.is_file():
                return candidate

        raise OSError(f"Could not find file {filename} in defined system include paths: "
                      f"{symtable.SYSTEM_INCLUDE_PATHS}")

    def preprocess(self, lines: Optional[List[str]] = None) -> str:
        "This will be a lie for a while. I'll have to fix it later."

        if lines:
            lines[-1] = lines[-1] + 'static_assert(false, "include node not properly implemented")'
        if self.system_include:
            found_path = PreprocessorIncludeNode.search_system_includes(self.target)
            symtable.FILE_STACK.append(open(found_path, 'r'))

        else:
            symtable.FILE_STACK.append(open(os.path.split(symtable.FILE_STACK[-1].name)[0]
                                            + '/' + self.target, 'r'))

        return 'static_assert(false, "include node not properly implemented")'


class IdentifierNode(Node):

    def __init__(self, children: List[str] = [], args: Any = None, variadic: bool = False) -> None:
        super(IdentifierNode, self).__init__("Identifier", children)
        self.args = args
        self.variadic = variadic

    def __str__(self) -> str:
        return f"{self.name}: {self.children}"

    def preprocess(self, lines: Any = None) -> str:
        expansion = ""
        if self.children[0] in symtable.TABLE.keys():
            expansion = symtable.TABLE[self.children[0]].expand(
                [arg.preprocess() for arg in self.args] if self.args is not None else None)
        else:
            if self.args is not None:
                expansion = f'{self.children[0]}({",".join([arg.preprocess() for arg in self.args])})'  # NOQA
            else:
                expansion = self.children[0]
        if lines:
            lines[-1] = lines[-1] + expansion

        return expansion


class PrimitiveNode(Node):
    def __init__(self, name: str, children: List[str] = []) -> None:
        super(PrimitiveNode, self).__init__(name, children)

    def __str__(self) -> str:
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines: Any = None) -> str:
        if lines:
            lines[-1] += self.children[0]
        return self.children[0]


class NewlineNode(PrimitiveNode):

    def __init__(self, children: List[str] = []) -> None:
        super(NewlineNode, self).__init__("Newline", children)

    def __str__(self) -> str:
        return "NewlineNode"

    def preprocess(self, lines: Optional[List[str]] = None) -> str:
        if lines:
            lines.append("")
        return "\n"


class WhiteSpaceNode(PrimitiveNode):

    def __init__(self, children: List[str] = []) -> None:
        super(WhiteSpaceNode, self).__init__("Whitespace", children)


class ASCIILiteralNode(PrimitiveNode):

    def __init__(self, children: List[str] = []) -> None:
        super(ASCIILiteralNode, self).__init__('ASCIILit', children)


class StringLiteralNode(PrimitiveNode):

    def __init__(self, children: List[str] = []) -> None:
        super(StringLiteralNode, self).__init__('StringLit', children)


class PreprocessingNumberNode(PrimitiveNode):

    def __init__(self, children: List[str] = []) -> None:
        super(PreprocessingNumberNode, self).__init__("PreprocessingNumber", children)
