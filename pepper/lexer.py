#! /usr/bin/env python3
import sys
import ply.lex as lex

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

print("tokens defined, {}".format(tokens))


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
    return t


def t_WHITESPACE(t):
    r"[\t ]"
    return t


def t_error(t):
    print("Unknown token on line {}: {}".format(t.lexer.lineno, t.value[0]))
    exit(1)


lexer = lex.lex()


def main():
    ilines = []
    for line in sys.stdin:
        ilines.append(line)
        # lexer.input(line)

    # terribly inefficient, but needed
    lexer.input("".join(ilines))

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


if __name__ == '__main__':
    main()
