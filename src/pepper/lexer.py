#! /usr/bin/env python3

# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This is the lexer for PEPPr

It's responsible for tokenizing the incoming character stream. The Parser will ingest the
token stream and build a tree, which will in turn produce actual c++ or c code.
"""

import sys
import ply.lex as lex
# from ply.lex.LexToken import lex.LexToken
import argparse
import pepper.symbol_table as symtable
from typing import List, Union

DEFAULT_LITERALS = ['+', '-', '*', '/', '|', '&', '(',
                    ')', '=', ',', '{', '}', '[', ']',
                    '.', ';', '!', '<', '>', ':', '~',
                    '^', '@', '#', '&', "'", '%', "?", "\\"]


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
    'if',
    'py',
    'error',
    'warning',
    'pragma'
]

tokens = [
    'BOOL_AND',
    'BOOL_OR',
    'CHAR_LITERAL',
    'COMP_EQU',
    'COMP_GTE',
    'COMP_LTE',
    'COMP_NEQU',
    'DEFINED',
    'IDENTIFIER',
    'INT_LITERAL',
    'L_SHIFT',
    'LONG_COMMENT',
    'NEWLINE',
    'OTHER',
    'PREPROCESSING_NUMBER',
    'PUNCTUATOR',
    'R_SHIFT',
    'STRING_LITERAL',
    'SYSTEM_INCLUDE_LITERAL',
    'WHITESPACE',
    # 'SKIPPED_LINE',
]

tokens.extend([f"PREPROCESSING_KEYWORD_{i.upper()}" for i in PREPROCESSING_KEYWORDS])


def t_PREPROCESSING_KEYWORD_PY(t: lex.LexToken) -> lex.LexToken:
    r"\#py\b"
    return t


def t_COMMENT(t: lex.LexToken) -> lex.LexToken:
    r"\s//.*"
    pass


def t_COMMENT_NO_WHITESPACE(t: lex.LexToken) -> lex.LexToken:
    r"//.*"
    pass


def t_PREPROCESSING_KEYWORD_IFDEF(t: lex.LexToken) -> lex.LexToken:
    r'\#ifdef\b'
    return t


def t_PREPROCESSING_KEYWORD_IFNDEF(t: lex.LexToken) -> lex.LexToken:
    r'\#ifndef\b'
    return t


def t_PREPROCESSING_KEYWORD_ENDIF(t: lex.LexToken) -> lex.LexToken:
    r'\#endif\b'
    return t


def t_PREPROCESSING_KEYWORD_IF(t: lex.LexToken) -> lex.LexToken:
    r'\#if\b'
    return t


def t_PREPROCESSING_KEYWORD_ELSE(t: lex.LexToken) -> lex.LexToken:
    r'\#else\b'
    return t


def t_PREPROCESSING_KEYWORD_INCLUDE(t: lex.LexToken) -> lex.LexToken:
    r'\#include\b'
    return t


def t_PREPROCESSING_KEYWORD_DEFINE(t: lex.LexToken) -> lex.LexToken:
    r'\#define\b'
    return t


def t_PREPROCESSING_KEYWORD_ERROR(t: lex.LexToken) -> lex.LexToken:
    r'\#error\b'
    return t


def t_PREPROCESSING_KEYWORD_PRAGMA(t: lex.LexToken) -> lex.LexToken:
    r'\#pragma\b'
    return t


def t_PREPROCESSING_KEYWORD_WARNING(t: lex.LexToken) -> lex.LexToken:
    r'\#warning\b'
    return t


def t_DEFINED(t: lex.LexToken) -> lex.LexToken:
    r'defined'
    return t


def t_SYSTEM_INCLUDE_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r"""<[^\'\"<>]*?>"""
    return t


def t_IDENTIFIER(t: lex.LexToken) -> lex.LexToken:
    r'([_a-zA-Z][_a-zA-Z0-9]*(\.\.\.)?)|(\.\.\.)'
    return t


def t_INT_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r'[0-9]+'
    return t


def t_PREPROCESSING_NUMBER(t: lex.LexToken) -> lex.LexToken:
    r'\.?[0-9]([0-9]|(e\+)|(e\-)|(E\+)|(E\-)|(p\+)|(p\-)|(P\+)|(P\-)|[a-zA-Z])*'
    return t


def t_COMP_LTE(t: lex.LexToken) -> lex.LexToken:
    r"<="
    return t


def t_COMP_GTE(t: lex.LexToken) -> lex.LexToken:
    r">="
    return t


def t_COMP_EQU(t: lex.LexToken) -> lex.LexToken:
    r"=="
    return t


def t_COMP_NEQU(t: lex.LexToken) -> lex.LexToken:
    r"!="
    return t


def t_BOOL_AND(t: lex.LexToken) -> lex.LexToken:
    r"&&"
    return t


def t_BOOL_OR(t: lex.LexToken) -> lex.LexToken:
    r"\|\|"
    return t


def t_L_SHIFT(t: lex.LexToken) -> lex.LexToken:
    r"<<"
    return t


def t_R_SHIFT(t: lex.LexToken) -> lex.LexToken:
    r">>"
    return t


def t_CHAR_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r"'(?:[^\\'] | \\.)'"
    return t


def t_STRING_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r"""('((\\['tn])|[^'\\])*')|("((\\["tn])|[^"\\])*")"""
    return t


def t_LONG_COMMENT_START(t: lex.LexToken) -> lex.LexToken:
    r"\/\*"
    t.lexer.begin('comment')
    pass


def t_comment_BLOCK_COMMENT_END(t: lex.LexToken) -> lex.LexToken:
    r"\*\/"
    t.lexer.begin('INITIAL')  # reset to initial state
    pass


def t_comment_ignore_anything_else(t: lex.LexToken) -> lex.LexToken:
    r".+?"
    pass


def t_comment_NEWLINE(t: lex.LexToken) -> lex.LexToken:
    r'\n'
    t.lexer.lineno += 1  # the lexer doesn't know what consistutes a 'line' unless we tell it
    symtable.LINE_COUNT += 1
    return t


def t_comment_error(t: lex.LexToken) -> lex.LexToken:
    raise symtable.PepperSyntaxError(f"Unknown token on line {t.lexer.lineno}: {t.value[0]}")


# TODO: maybe convert this to a t_ignore() rule for improved lexing performance
def t_NEWLINE(t: lex.LexToken) -> lex.LexToken:
    r"\n"
    t.type = 'NEWLINE'
    t.lexer.lineno += 1  # the lexer doesn't know what consistutes a 'line' unless we tell it
    symtable.LINE_COUNT += 1
    return t


def t_WHITESPACE(t: lex.LexToken) -> lex.LexToken:
    r"[\t ]"
    return t


def t_error(t: lex.LexToken) -> lex.LexToken:
    raise symtable.PepperSyntaxError(f"Unknown token on line {t.lexer.lineno}: {t.value[0]}")


lexer = lex.lex()
ignore = ['WHITESPACE', 'NEWLINE']


def lex(lines: List[str], debug_mode: bool = False) -> None:
    "Takes a single string, containing newlines, that's the entire input"
    lexer.input(lines)

    arcade: List[lex.LexToken] = []
    tok: Union[lex.LexToken, bool] = True
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


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="The file to lex")
    parser.add_argument('--debug_mode', action='store_true')
    return parser.parse_args()


def main() -> None:
    args = get_args()

    lex(args.input_file.read(), args.debug_mode)


if __name__ == '__main__':
    main()
