import pepper.parser as parser
# from collections import defaultdict


def get_all_tokens(given_lexer):
    tokens = []
    while True:
        tok = given_lexer.token()
        if not tok:
            break
        tokens.append(tok)

    return tokens


def test_lexer_basic_example():
    test_lines = open('tests/test_data/system_include.cpp', 'r').readlines()
    parse_tree = parser.parse("\n".join(test_lines))
    print(parse_tree)