
"""
This is the abstract symbol tree for PEPPr.

The parser will build the actual tree, so this is really more of a library of nodes that may
be used within the tree.
"""


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


class StatementsNode(Node):

    def __init__(self, children=None):
        super(StatementsNode, self).__init__("Statements", children)

    def preprocess(self, lines):
        for child in self.children:
            child.preprocess(lines)


class PreprocessorDirectiveNode(Node):

    def __init__(self, children):
        super(PreprocessorDirectiveNode, self).__init__("PreprocessorDirective", children)


class PreprocessorIncludeNode(Node):

    def __init__(self, children, system_include=False):
        super(PreprocessorIncludeNode, self).__init__("PreprocessorInclude", children)
        self.system_incude = system_include
        self.target = children[0]

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines):
        "This will be a lie for a while. I'll have to fix it later."
        lines[-1] = lines[-1] + 'static_assert(false, "include node not properly implemented")'


class IdentifierNode(Node):

    def __init__(self, children):
        super(IdentifierNode, self).__init__("Identifier", children)

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines):
        lines[-1] = lines[-1] + self.children[0]


class NewlineNode(Node):

    def __init__(self, children):
        super(NewlineNode, self).__init__("Newline", children)

    def __str__(self):
        return "NewlineNode"

    def preprocess(self, lines):
        lines.append("")


class WhiteSpaceNode(Node):

    def __init__(self, children):
        super(WhiteSpaceNode, self).__init__("Whitespace", children)

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines):
        lines[-1] += self.children[0]


class ASCIILiteralNode(Node):

    def __init__(self, children):
        super(ASCIILiteralNode, self).__init__('ASCIILit', children)

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines):
        lines[-1] = lines[-1] + self.children[0]


class PreprocssingNumberNode(Node):

    def __init__(self, children):
        super(PreprocssingNumberNode, self).__init__("PreprocessingNumber", children)

    def __str__(self):
        return f"{self.name}: {self.children[0]}"

    def preprocess(self, lines):
        lines[-1] = lines[-1] + self.children[0]
