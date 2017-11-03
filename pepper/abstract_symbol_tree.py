
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

    def __str__(self, depth=0, lines):
        lines = ["{}Node: {}".format("\t"*depth, self.name)]

        for child in self.children:
