import pepper.parser as parser
import sys
import subprocess
# from collections import defaultdict


def get_all_tokens(given_lexer):
    tokens = []
    while True:
        tok = given_lexer.token()
        if not tok:
            break
        tokens.append(tok)

    return tokens


class TestUnit(object):
    def test_parser_system_include_example(self):
        test_lines = open('tests/test_data/system_include.cpp', 'r').readlines()
        parse_tree = parser.parse("\n".join(test_lines))
        print(parse_tree, file=sys.stderr)

    def test_parser_file_include_example(self):
        test_lines = open('tests/test_data/file_include.cpp', 'r').readlines()
        parse_tree = parser.parse("\n".join(test_lines))
        print(parse_tree, file=sys.stderr)

    def test_parser_error(self):
        test_lines = open('tests/test_data/error.cpp', 'r').readlines()
        exception_caught = False
        parse_tree = None
        try:
            parse_tree = parser.parse("\n".join(test_lines))
        except Exception:
            exception_caught = True
        assert(exception_caught)
        print(parse_tree, file=sys.stderr)


class TestSystem(object):
    def test_parser_command_line_call(self):
        process = subprocess.Popen(["PepperParse", "./tests/test_data/file_include.cpp"],
                                   stdout=subprocess.PIPE)
        out, err = process.communicate()
        assert(out == b"Node: Statements\n\tNode: PreprocessorInclude\n\t'SomeFile.h'\n")
