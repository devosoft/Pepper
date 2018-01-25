import pepper.parser as parser
import sys


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


#  Do you like my super long literals?
file_include_parse_results = b"""Node: Statements
\tPreprocessorInclude:
\tNewlineNode
\tNewlineNode
\tIdentifier: int
\tWhitespace:
\tIdentifier: main
\tASCIILit: (
\tASCIILit: )
\tWhitespace:
\tASCIILit: {
\tNewlineNode
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tIdentifier: int
\tWhitespace:
\tIdentifier: x
\tWhitespace:
\tASCIILit: =
\tWhitespace:
\tPreprocessingNumber: 3
\tASCIILit: ;
\tNewlineNode
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tIdentifier: int
\tWhitespace:
\tIdentifier: sum
\tWhitespace:
\tASCIILit: =
\tWhitespace:
\tPreprocessingNumber: 0
\tASCIILit: ;
\tNewlineNode
\tNewlineNode
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tIdentifier: for
\tASCIILit: (
\tIdentifier: int
\tWhitespace:
\tIdentifier: i
\tWhitespace:
\tASCIILit: =
\tWhitespace:
\tPreprocessingNumber: 0
\tASCIILit: ;
\tWhitespace:
\tIdentifier: i
\tWhitespace:
\tASCIILit: <
\tWhitespace:
\tIdentifier: x
\tASCIILit: ;
\tWhitespace:
\tIdentifier: i
\tASCIILit: +
\tASCIILit: +
\tASCIILit: )
\tWhitespace:
\tASCIILit: {
\tNewlineNode
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tIdentifier: sum
\tWhitespace:
\tASCIILit: +
\tASCIILit: =
\tWhitespace:
\tIdentifier: i
\tASCIILit: ;
\tNewlineNode
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tASCIILit: }
\tNewlineNode
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tWhitespace:
\tIdentifier: return
\tWhitespace:
\tIdentifier: sum
\tASCIILit: ;
\tNewlineNode
\tASCIILit: }
"""
