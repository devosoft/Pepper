#! /usr/bin/env python3

"""
This is the lexer for PEPPr

It's responsible for tokenizing the incoming character stream. The Parser will ingest the
token stream and build a tree, which will in turn produce actual c++ or c code.
"""
import sys
import ply.lex as lex
import argparse

literals = ['+', '-', '*', '/', '(', ')',
            '=', ',', '{', '}', '[', ']',
            '.', ';', '!', '#', '<', '>', ':', '~']


PREPROCESSING_KEYWORDS = [
    'include',
    'define'
]

tokens = [
    'IDENTIFIER',
    'NEWLINE',
    'OTHER',
    'PREPROCESSING_NUMBER',
    'PUNCTUATOR',
    # 'SKIPPED_LINE',
    'STRING_LITERAL',
    'WHITESPACE',
]

tokens.extend([f"PREPROCESSING_KEYWORD_{i.upper()}" for i in PREPROCESSING_KEYWORDS])


def t_PREPROCESSING_KEYWORD_INCLUDE(t):
    r'include'
    return t


def t_PREPROCESSING_KEYWORD_DEFINE(t):
    r'define'
    return t


def t_IDENTIFIER(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'
    return t


def t_PREPROCESSING_NUMBER(t):
    r'\.?[0-9]([0-9]|(e\+)|(e\-)|(E\+)|(E\-)|(p\+)|(p\-)|(P\+)|(P\-)|[a-zA-Z])*'
    return t


def t_STRING_LITERAL(t):
    r"""('((\\['"tn])|[^'"\\])*')|("((\\['"tn])|[^'"\\])*")"""
    return t


# def t_SKIPPED_LINE(t):
#     r"\\\n"
#     return t


# TODO: maybe convert this to a t_ignore() rule for improved lexing performance
def t_NEWLINE(t):
    r"\n"
    t.type = 'NEWLINE'
    t.lexer.lineno += 1  # the lexer doesn't know what consistutes a 'line' unless we tell it
    return t


def t_WHITESPACE(t):
    r"[\t ]"
    return t


def t_error(t):
    print(f"Unknown token on line {t.lexer.lineno}: {t.value[0]}")
    exit(1)


lexer = lex.lex()
ignore = ['WHITESPACE', 'NEWLINE']


def lex(lines, debug_mode=False):
    "Takes a single string, containing newlines, that's the entire input"
    # lexer.input("".join(ilines))
    lexer.input(lines)

    arcade = []
    tok = True
    while True:
        tok = lexer.token()
        if not tok:
            break  # end of file reached
        arcade.append(tok)

    for token in arcade:
        try:
            if token.type in ignore:
                if debug_mode:
                    print(f"(IGNORED:) {token.type}: {token.value}")
                else:
                    continue
            elif token.type in literals:
                print(f"ASCII_LITERAL: {token.value}")
            elif token.type != 'UNKNOWN':
                print(f"{token.type}: {token.value}")
            else:
                print(f"Unknown token in input: {token.value}")
                sys.exit(1)
        except: # NOQA
            print(f'Blew up trying to access type of {token}')

    return 0


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType('r'), help="The file to lex")
    parser.add_argument('--debug_mode', action='store_true')
    return parser.parse_args()


def main():
    args = get_args()

    lex(args.input_file.read(), args.debug_mode)


if __name__ == '__main__':
    main()
