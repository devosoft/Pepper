# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This is the abstract symbol tree for PEPPr.

The parser will build the actual tree, so this is really more of a library of nodes that may
be used within the tree.
"""
import pepper.symbol_table as symtable
import os

from pathlib import Path


class Node():
    def __init__(self, name="Node", children=None):
        self.name = name
        if children:
            self.children = children
        else:
            self.children = []

    def __str__(self):
        lines = [f"Node: {self.name}"]

        for child in self.children:
            lines.append(f"\t{str(child)}")

        return "\n".join(lines)

    def preprocess(self, lines):
        raise NotImplementedError()


class LinesNode(Node):

    def __init__(self, children=None):
        if children is not None:
            # sometimes whitespace is none, oops
            children = [child for child in children if child is not None]
        super(LinesNode, self).__init__("Statements", children)

    def preprocess(self, lines=None):
        if lines:
            for child in self.children:
                child.preprocess(lines)
        else:
            return "".join([r.preprocess() for r in self.children])


class PreprocessorDirectiveNode(Node):

    def __init__(self, children):
        super(PreprocessorDirectiveNode, self).__init__("PreprocessorDirective", children)


class PreprocessorIncludeNode(Node):

    def __init__(self, children, system_include=False):
        super(PreprocessorIncludeNode, self).__init__("PreprocessorInclude", children)
        self.system_include = system_include
        self.target = children[0][1:-1]

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def search_system_includes(filename):
        for system_path in symtable.SYSTEM_INCLUDE_PATHS:
            candidate = Path(f"{system_path}/{filename}")
            if candidate.exists() and candidate.is_file():
                return candidate

        raise OSError(f"Could not find file {filename} in defined system include paths: "
                      f"{symtable.SYSTEM_INCLUDE_PATHS}")

    def preprocess(self, lines):
        "This will be a lie for a while. I'll have to fix it later."

        lines[-1] = lines[-1] + 'static_assert(false, "include node not properly implemented")'
        if self.system_include:
            found_path = PreprocessorIncludeNode.search_system_includes(self.target)
            symtable.FILE_STACK.append(open(found_path, 'r'))

        else:
            symtable.FILE_STACK.append(open(os.path.split(symtable.FILE_STACK[-1].name)[0]
                                            + '/' + self.target, 'r'))


class IdentifierNode(Node):

    def __init__(self, children, args=None):
        super(IdentifierNode, self).__init__("Identifier", children)
        self.args = args

    def __str__(self):
        return f"{self.name}: {self.children}"

    def preprocess(self, lines=None):
        expansion = self.children[0]
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
        else:
            return expansion


class PrimitiveNode(Node):
    def __init__(self, name, children):
        super(PrimitiveNode, self).__init__(name, children)

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines=None):
        if lines:
            lines[-1] += self.children[0]
        else:
            return self.children[0]


class NewlineNode(PrimitiveNode):

    def __init__(self, children):
        super(NewlineNode, self).__init__("Newline", children)

    def __str__(self):
        return "NewlineNode"

    def preprocess(self, lines):
        lines.append("")


class WhiteSpaceNode(PrimitiveNode):

    def __init__(self, children):
        super(WhiteSpaceNode, self).__init__("Whitespace", children)


class ASCIILiteralNode(PrimitiveNode):

    def __init__(self, children):
        super(ASCIILiteralNode, self).__init__('ASCIILit', children)


class StringLiteralNode(PrimitiveNode):

    def __init__(self, children):
        super(StringLiteralNode, self).__init__('StringLit', children)


class PreprocessingNumberNode(PrimitiveNode):

    def __init__(self, children):
        super(PreprocessingNumberNode, self).__init__("PreprocessingNumber", children)
