import pepper.lexer as lexer
import pepper.parser as parser
from collections import defaultdict


def get_all_tokens(given_lexer):
    tokens = []
    while True:
        tok = given_lexer.token()
        if not tok:
            break
        tokens.append(tok)

    return tokens


def test_lexer_basic_example():
    test_lines = open('pepper/tests/test_data/example.cpp', 'r').readlines()
    lexer.lexer.input('\n'.join(test_lines))
    tokens = get_all_tokens(lexer.lexer)

    assert(len(tokens) == 8)

    token_types = defaultdict(int)

    for token in tokens:
        token_types[token.type] += 1

    assert(token_types['CODE'] == 4)
    assert(token_types['C_PREPROCESSOR_DIRECTIVE'] == 2)
    assert(token_types['PEPPER_DIRECTIVE'] == 2)
