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


#  Do you like my super long literals?
file_include_parse_results = b"""Node: Statements
\tPreprocessorInclude: 'SomeFile.h'
\tIdentifier: int
\tIdentifier: main
\t(
\t)
\t{
\tIdentifier: int
\tIdentifier: x
\t=
\tPreprocessingNumber: 3
\t;
\tIdentifier: int
\tIdentifier: sum
\t=
\tPreprocessingNumber: 0
\t;
\tIdentifier: for
\t(
\tIdentifier: int
\tIdentifier: i
\t=
\tPreprocessingNumber: 0
\t;
\tIdentifier: i
\t<
\tIdentifier: x
\t;
\tIdentifier: i
\t+
\t+
\t)
\t{
\tIdentifier: sum
\t+
\t=
\tIdentifier: i
\t;
\t}
\tIdentifier: return
\tIdentifier: sum
\t;
\t}
"""


class TestSystem(object):
    def test_parser_command_line_call(self):
        process = subprocess.Popen(["PepperParse", "./tests/test_data/file_include.cpp"],
                                   stdout=subprocess.PIPE)
        out, err = process.communicate()
        assert(out == file_include_parse_results)
