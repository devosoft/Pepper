#! /usr/bin/env python3

# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This module handles the lexing of the C/C++ preprocessing language
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
] + [f"PREPROCESSING_KEYWORD_{keyword.upper()}" for keyword in PREPROCESSING_KEYWORDS]


def t_IDENTIFIER(t: lex.LexToken) -> lex.LexToken:
    r'([_a-zA-Z][_a-zA-Z0-9]*(\.\.\.)?)|(\.\.\.)'

    if t.value in PREPROCESSING_KEYWORDS:
        t.type = f"PREPROCESSING_KEYWORD_{t.value.upper()}"

    return t


def t_INT_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r'[0-9]+L?'
    if t.value[-1] == 'L':
        t.value = t.value[:-1]
    return t


def t_PREPROCESSING_NUMBER(t: lex.LexToken) -> lex.LexToken:
    r'\.?[0-9]([0-9]|(e\+)|(e\-)|(E\+)|(E\-)|(p\+)|(p\-)|(P\+)|(P\-)|[a-zA-Z])*'
    return t


def t_SYSTEM_INCLUDE_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r"""<[^\'\"<>]*?>"""
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


def t_STRING_LITERAL(t: lex.LexToken) -> lex.LexToken:
    r"""('((\\['tn])|[^'\\])*')|("((\\["tn])|[^"\\])*")"""
    return t


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
