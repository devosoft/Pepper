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
            '.', ';', '!', '#', '<', '>', ':']


PREPROCESSING_KEYWORDS = [
    'include',
    'define'
]

tokens = [
    'IDENTIFIER',
    'PREPROCESSING_NUMBER',
    'STRING_LITERAL',
    'PUNCTUATOR',
    'WHITESPACE',
    'OTHER',
]

tokens.extend(["PREPROCESSING_KEYWORD_{}".format(i.upper()) for i in PREPROCESSING_KEYWORDS])

# print("tokens defined, {}".format(tokens))


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


# def t_PUNCTUATOR(t):
#     r"""[{}:;,?%&*<>=#/!]|[\[\]\(\)\.\^\-\|\+]"""
#     return t


# TODO: maybe convert this to a t_ignore() rule for improved lexing performance
def t_NEWLINE(t):
    "[\n]"
    t.type = 'WHITESPACE'
    t.lexer.lineno += 1  # the lexer doesn't know what consistutes a 'line' unless we tell it
    pass


def t_WHITESPACE(t):
    r"[\t ]"
    pass


def t_error(t):
    print("Unknown token on line {}: {}".format(t.lexer.lineno, t.value[0]))
    exit(1)


lexer = lex.lex()



def lex(lines):
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

    print(arcade)

    ignore = ['WHITESPACE']

    for token in arcade:
        try:
            if token.type in ignore:
                continue
            elif token.type in literals:
                print("ASCII_LITERAL: {}".format(token.value))
            elif token.type != 'UNKNOWN':
                print("{}: {}".format(token.type, token.value))
            else:
                print("Unknown token in input: {}".format(token.value))
                sys.exit(1)
        except:
            print('Blew up trying to access type of {}'.format(token))

    return 0


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType('r'), help="The file to lex")
    # parser.add_argument('--debug_mode', action='store_true')
    return parser.parse_args()


def main():
    args = get_args()

    lex(args.input_file.read())


if __name__ == '__main__':
    main()
