# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

import pepper.symbol_table as symtable
import pepper.abstract_symbol_tree as ast
import utils as testutils


class TestUnit():
    def test_macro_expansion_bad_number_of_args(self):
        alpha = ast.IdentifierNode(['alpha'])
        omega = ast.IdentifierNode(['omega'])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])
        macro = symtable.MacroExpansion('foo',
                                        [alpha, whitespace, plus, whitespace, omega],
                                        ['alpha', 'omega'])

        testutils.assert_raises(macro.expand,
                                symtable.PepperSyntaxError,
                                ["Wrong number of arguments in macro expansion for foo",
                                 "expected 2",
                                 "got 0"],
                                args=[])

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

    def test_macro_expansion_bad_variadic_position(self):
        alpha = ast.IdentifierNode(["alpha"])
        omega = ast.IdentifierNode(["omega"])
        vary_expand = ast.IdentifierNode(["vary"])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])

        testutils.assert_raises(symtable.MacroExpansion,
                                symtable.PepperSyntaxError,
                                ["Variadic macro argument must be at the end of the argument definition list"], # NOQA
                                'foo',
                                [alpha, whitespace, plus, whitespace, omega, plus, vary_expand],
                                ['alpha', 'omega', 'varia...', 'extra...'])

        testutils.assert_raises(symtable.MacroExpansion,
                                symtable.PepperSyntaxError,
                                ["Variadic macro argument must be at the end of the argument definition list"], # NOQA
                                'foo',
                                [alpha, whitespace, plus, whitespace, omega, plus, vary_expand],
                                ['alpha', 'omega', 'varia...', 'notvaria'])

    def test_macro_expansion_variadic_too_few_args(self):
        alpha = ast.IdentifierNode(["alpha"])
        omega = ast.IdentifierNode(["omega"])
        vary_expand = ast.IdentifierNode(["vary"])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])

        macro = symtable.MacroExpansion('notfoo',
                                        [alpha, whitespace, plus, whitespace,
                                         omega, plus, vary_expand],
                                        ['alpha', 'omega', 'varia...'])

        testutils.assert_raises(macro.expand,
                                symtable.PepperSyntaxError,
                                ["notfoo was given 2 arguments, but takes a minimum of 4"], # NOQA
                                [1, 2])

    def test_macro_expansion_variadic(self):
        alpha = ast.IdentifierNode(["alpha"])
        omega = ast.IdentifierNode(["omega"])
        vary_expand = ast.IdentifierNode(["vary"])
        whitespace = ast.WhiteSpaceNode([' '])
        plus = ast.ASCIILiteralNode(['+'])

        macro = symtable.MacroExpansion('alsonotfoo',
                                        [alpha, whitespace, plus, whitespace,
                                         omega, plus, vary_expand],
                                        ['alpha', 'omega', 'varia...'])

        expansion = macro.expand(args=[1, 2, 3, 4, 5, 6, 7, 8, 9])
        assert(expansion == "1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9")
