#! /usr/bin/env python3

"""
This is the lexer for PEPPr

It's responsible for tokenizing the incoming character stream. The Parser will ingest the
token stream and build a tree, which will in turn produce actual c++ or c code.
"""
import sys
import ply.lex as lex
import argparse

DEFAULT_LITERALS = ['+', '-', '*', '/', '(', ')',
                    '=', ',', '{', '}', '[', ']',
                    '.', ';', '!', '<', '>', ':', '~',
                    '@', '#', '&', "'"]


literals = DEFAULT_LITERALS

states = [
    # recall there's also the default INITIAL state
    ('comment', 'exclusive')
]

PREPROCESSING_KEYWORDS = [
    'include',
    'define',
    'ifdef',
    'ifndef',
    'endif',
    'else',
    'py',
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
    'LONG_COMMENT',
    'SYSTEM_INCLUDE_LITERAL'
]

tokens.extend([f"PREPROCESSING_KEYWORD_{i.upper()}" for i in PREPROCESSING_KEYWORDS])


def t_PREPROCESSING_KEYWORD_PY(t):
    r"\#py\b"
    return t


def t_COMMENT(t):
    r"\s//.*"
    pass


def t_COMMENT_NO_WHITESPACE(t):
    r"//.*"
    pass


def t_PREPROCESSING_KEYWORD_IFDEF(t):
    r'\#ifdef\b'
    return t


def t_PREPROCESSING_KEYWORD_IFNDEF(t):
    r'\#ifndef\b'
    return t


def t_PREPROCESSING_KEYWORD_ENDIF(t):
    r'\#endif\b'
    return t


def t_PREPROCESSING_KEYWORD_ELSE(t):
    r'\#else\b'
    return t


def t_PREPROCESSING_KEYWORD_INCLUDE(t):
    r'\#include\b'
    return t


def t_PREPROCESSING_KEYWORD_DEFINE(t):
    r'\#define\b'
    return t


def t_SYSTEM_INCLUDE_LITERAL(t):
    r"""<[^\'\"<>]*?>"""
    return t


def t_IDENTIFIER(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'
    return t


def t_PREPROCESSING_NUMBER(t):
    r'\.?[0-9]([0-9]|(e\+)|(e\-)|(E\+)|(E\-)|(p\+)|(p\-)|(P\+)|(P\-)|[a-zA-Z])*'
    return t


def t_STRING_LITERAL(t):
    r"""('((\\['tn])|[^'\\])*')|("((\\["tn])|[^"\\])*")"""
    return t


def t_LONG_COMMENT_START(t):
    r"\/\*"
    t.lexer.begin('comment')
    pass


def t_comment_BLOCK_COMMENT_END(t):
    r"\*\/"
    t.lexer.begin('INITIAL')  # reset to initial state
    pass


def t_comment_ignore_anything_else(t):
    r".+?"
    pass


def t_comment_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1  # the lexer doesn't know what consistutes a 'line' unless we tell it
    return t


def t_comment_error(t):
    raise Exception(f"Unknown token on line {t.lexer.lineno}: {t.value[0]}")


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
    raise Exception(f"Unknown token on line {t.lexer.lineno}: {t.value[0]}")


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
