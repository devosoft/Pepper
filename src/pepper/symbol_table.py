"""
The Symbol Table module implements a class to track declarations and usages of identifiers
"""


class MacroExpansion():
    def __init__(self, name, expansion, args=[]):
        self.name = name
        self.expansion = expansion
        self.args = args

    def expand(self, args=[]):
        if len(args) != len(self.args):
            raise SyntaxError(f"Wrong number of arguments in macro expansion for {self.name};"
                              f" expected {len(self.args)}, got {len(args)}")
        expansion = self.expansion
        for index, arg in enumerate(args):
            expansion = expansion.replace(self.args[index], str(arg))
        return expansion

    def __str__(self):
        return f"Macro {self.name} with args {self.args} expanding to '{self.expansion}'"


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
