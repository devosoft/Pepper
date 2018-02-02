# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

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

        assert(len(tokens) == 76)

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
            '#': 0,
            '+': 1,
            '<': 12,
            '=': 2,
            'IDENTIFIER': 22,
            'PREPROCESSING_KEYWORD_DEFINE': 1,
            'PREPROCESSING_KEYWORD_INCLUDE': 1,
            'PREPROCESSING_NUMBER': 4,
            'STRING_LITERAL': 4,
            'SYSTEM_INCLUDE_LITERAL': 1
        }

        for token_type, count in tokens_to_assert.items():
            assert(token_types[token_type] == count)

    def test_lexer_unknown_token(self):
        test_lines = open('tests/test_data/unknown_token.cpp', 'r').readlines()
        lexer.lexer.input('\n'.join(test_lines))
        try:
            tokens = get_all_tokens(lexer.lexer) # NOQA
            assert(False and "Above line should have filed!")
        except Exception as err:
            assert(str(err) == "Unknown token on line 24: ©")


class TestSystem(object):
    def test_lexer_command_line(self):
        process = subprocess.Popen(["PepperLex", "./tests/test_data/file_include.cpp"],
                                   stdout=subprocess.PIPE)
        out, err = process.communicate()
        expected_out = b"""\
PREPROCESSING_KEYWORD_INCLUDE: #include
STRING_LITERAL: 'SomeFile.h'
PREPROCESSING_KEYWORD_DEFINE: #define
IDENTIFIER: POTATO
PREPROCESSING_NUMBER: 12345
PREPROCESSING_KEYWORD_DEFINE: #define
IDENTIFIER: FOO
PREPROCESSING_NUMBER: 12345
ASCII_LITERAL: >
PREPROCESSING_NUMBER: 4578
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
IDENTIFIER: if
ASCII_LITERAL: (
IDENTIFIER: SomeOtherFileIncluded
ASCII_LITERAL: )
ASCII_LITERAL: {
IDENTIFIER: return
IDENTIFIER: sum
ASCII_LITERAL: ;
ASCII_LITERAL: }
IDENTIFIER: else
ASCII_LITERAL: {
IDENTIFIER: return
ASCII_LITERAL: -
PREPROCESSING_NUMBER: 1
ASCII_LITERAL: ;
ASCII_LITERAL: }
ASCII_LITERAL: }
"""

        assert(out == expected_out)

    # def test_lexer_unknown_token(self):
    #     process = subprocess.Popen(["PepperLex", "./tests/test_data/unknown_token.cpp"],
    #                                stdout=subprocess.PIPE)
    #     out, err = process.communicate()
    #     # expected_out = b"Unknown token on line 1: \xc2\xa9\n"
    #     print(out, err)
    #     assert(b"Exception: Unknown token on line 1: @" in out)
    #     assert(process.returncode == 1)
