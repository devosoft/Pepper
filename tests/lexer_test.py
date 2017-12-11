import pepper.lexer as lexer
from pepper.lexer import ignore as tokens_to_ignore
from collections import defaultdict
import subprocess


def get_all_tokens(given_lexer):
    tokens = []
    while True:
        tok = given_lexer.token()
        if not tok:
            break
        if tok.type not in tokens_to_ignore:
            tokens.append(tok)

    return tokens


class TestUnit(object):
    def test_lexer_basic_example(self):
        test_lines = open('tests/test_data/example.cpp', 'r').readlines()
        lexer.lexer.input('\n'.join(test_lines))
        tokens = get_all_tokens(lexer.lexer)

        assert(len(tokens) == 82)

        token_types = defaultdict(int)

        for token in tokens:
            token_types[token.type] += 1

        print(token_types)

        tokens_to_assert = {
            ',': 1,
            ';': 2,
            ':': 8,
            '.': 3,
            '(': 4,
            ')': 4,
            '[': 1,
            ']': 1,
            '{': 1,
            '}': 1,
            '#': 4,
            '+': 1,
            '<': 13,
            '=': 2,
            '>': 1,
            'IDENTIFIER': 25,
            'PREPROCESSING_KEYWORD_DEFINE': 1,
            'PREPROCESSING_KEYWORD_INCLUDE': 1,
            'PREPROCESSING_NUMBER': 4,
            'STRING_LITERAL': 4,
        }

        for token_type, count in tokens_to_assert.items():
            assert(token_types[token_type] == count)


class TestSystem(object):
    def test_lexer_command_line(self):
        process = subprocess.Popen(["PepperLex", "./tests/test_data/file_include.cpp"],
                                   stdout=subprocess.PIPE)
        out, err = process.communicate()
        expected_out = b"""\
ASCII_LITERAL: #
PREPROCESSING_KEYWORD_INCLUDE: include
STRING_LITERAL: 'SomeFile.h'
IDENTIFIER: int
IDENTIFIER: main
ASCII_LITERAL: (
ASCII_LITERAL: )
ASCII_LITERAL: {
IDENTIFIER: int
IDENTIFIER: x
ASCII_LITERAL: =
PREPROCESSING_NUMBER: 3
ASCII_LITERAL: ;
IDENTIFIER: int
IDENTIFIER: sum
ASCII_LITERAL: =
PREPROCESSING_NUMBER: 0
ASCII_LITERAL: ;
IDENTIFIER: for
ASCII_LITERAL: (
IDENTIFIER: int
IDENTIFIER: i
ASCII_LITERAL: =
PREPROCESSING_NUMBER: 0
ASCII_LITERAL: ;
IDENTIFIER: i
ASCII_LITERAL: <
IDENTIFIER: x
ASCII_LITERAL: ;
IDENTIFIER: i
ASCII_LITERAL: +
ASCII_LITERAL: +
ASCII_LITERAL: )
ASCII_LITERAL: {
IDENTIFIER: sum
ASCII_LITERAL: +
ASCII_LITERAL: =
IDENTIFIER: i
ASCII_LITERAL: ;
ASCII_LITERAL: }
IDENTIFIER: return
IDENTIFIER: sum
ASCII_LITERAL: ;
ASCII_LITERAL: }
"""

        assert(out == expected_out)
