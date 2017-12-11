"""
The Symbol Table module implements a class to track declarations and usages of identifiers
"""


class SymbolTable():
    def __init__(self):
        self.table = dict()

    def declare_expansion(self, identifier, expansion):
        self.table[identifier] = expansion

    def use_expansion(self, identifier):
        if identifier in self.table.keys:
            return self.table[identifier]
        else:
            return None
