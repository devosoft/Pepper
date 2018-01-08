import pepper.symbol_table as symtable


class TestUnit():
    def test_macro_expansion_bad_number_of_args(self):
        macro = symtable.MacroExpansion('foo', 'alpha + omega', ['alpha', 'omega'])
        failed = False
        try:
            macro.expand(args=[])
        except SyntaxError as err:
            failed = True
            assert("Wrong number of arguments in macro expansion for foo" in err.msg)
            assert("expected 2" in err.msg)
            assert("got 0" in err.msg)

        assert(failed)

    def test_macro_expansion_good_number_of_args(selfself):
        macro = symtable.MacroExpansion('foo', 'alpha + omega', ['alpha', 'omega'])
        expansion = macro.expand(args=[1, 2])

        assert(expansion == "1 + 2")