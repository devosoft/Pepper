import pepper.symbol_table as symtable
import pepper.abstract_symbol_tree as ast


class TestUnit():
    def test_macro_expansion_bad_number_of_args(self):
        alpha = ast.IdentifierNode(['alpha'])
        omega = ast.IdentifierNode(['omega'])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])
        macro = symtable.MacroExpansion('foo',
                                        [alpha, whitespace, plus, whitespace, omega],
                                        ['alpha', 'omega'])
        failed = False
        try:
            macro.expand(args=[])
        except SyntaxError as err:
            failed = True
            assert("Wrong number of arguments in macro expansion for foo" in err.msg)
            assert("expected 2" in err.msg)
            assert("got 0" in err.msg)

        assert(failed)

    def test_macro_expansion_good_number_of_args(self):
        alpha = ast.IdentifierNode(['alpha'])
        omega = ast.IdentifierNode(['omega'])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])
        macro = symtable.MacroExpansion('foo',
                                        [alpha, whitespace, plus, whitespace, omega],
                                        ['alpha', 'omega'])
        expansion = macro.expand(args=[1, 2])

        assert(expansion == "1 + 2")

    def test_macro_expansion_bad_number_of_variadics(self):
        alpha = ast.IdentifierNode(["alpha"])
        omega = ast.IdentifierNode(["omega"])
        vary_expand = ast.IdentifierNode(["vary"])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])

        failed = False
        try:
            symtable.MacroExpansion('foo',
                                    [alpha, whitespace, plus, whitespace, omega, plus, vary_expand],
                                    ['alpha', 'omega', 'varia...', 'extra...'])
            assert(False and "Should have hit an exception")
        except symtable.PepperSyntaxError as err:
            failed = True
            assert("Cannot have multiple variadic arguments to a macro" in str(err))
        assert(failed)

    def test_macro_expansion_variadic(self):
        alpha = ast.IdentifierNode(["alpha"])
        omega = ast.IdentifierNode(["omega"])
        vary_expand = ast.IdentifierNode(["vary"])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])

        macro = symtable.MacroExpansion('notfoo',
                                        [alpha, whitespace, plus, whitespace,
                                         omega, plus, vary_expand],
                                        ['alpha', 'omega', 'varia...'])

        expansion = macro.expand(args=[1, 2, 3, 4, 5, 6, 7, 8, 9])
        assert(expansion == "1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9")
