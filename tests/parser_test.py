import pepper.parser as parser
import sys
# from collections import defaultdict


def get_all_tokens(given_lexer):
    tokens = []
    while True:
        tok = given_lexer.token()
        if not tok:
            break
        tokens.append(tok)

    return tokens


def test_parser_system_include_example():
    test_lines = open('tests/test_data/system_include.cpp', 'r').readlines()
    parse_tree = parser.parse("\n".join(test_lines))
    print(parse_tree, file=sys.stderr)


def test_parser_file_include_example():
    test_lines = open('tests/test_data/file_include.cpp', 'r').readlines()
    parse_tree = parser.parse("\n".join(test_lines))
    print(parse_tree, file=sys.stderr)


def test_parser_error():
    test_lines = open('tests/test_data/error.cpp', 'r').readlines()
    exception_caught = False
    parse_tree = None
    try:
        parse_tree = parser.parse("\n".join(test_lines))
    except Exception:
        exception_caught = True
    assert(exception_caught)
    print(parse_tree, file=sys.stderr)
