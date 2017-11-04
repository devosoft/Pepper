
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
        lines = ["Node: {}".format(self.name)]

        for child in self.children:
            lines.append("\t{}".format(str(child)))

        return "\n".join(lines)

    def preprocess(self, generated_code):
        raise NotImplementedError()


class StatementsNode(Node):
    # super(StatementsNode, self).__init__("Statements", None, children)

    def __init__(self, children=None):
        super(StatementsNode, self).__init__("Statements", children)

    def preprocess(self, generated_code):
        for child in self.children:
            child.preprocess(generated_code)


class PreprocessorDirectiveNode(Node):

    def __init__(self, children):
        super(PreprocessorDirectiveNode, self).__init__("PreprocessorDirective", children)

    def preprocess(self, generated_code):
        print("Imagine I preprocessed some stuff")
        return str(self)


class PreprocessorIncludeNode(Node):

    def __init__(self, children, system_include=False):
        super(PreprocessorIncludeNode, self).__init__("PreprocessorInclude", children)
        self.system_incude = system_include
        self.target = children[0]
