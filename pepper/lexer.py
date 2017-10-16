#! /usr/bin/env python3
import sys
import ply.lex as lex

tokens = [
    'IDENTIFIER',
    'PREPROCESSING_NUMBER',
    'STRING_LITERAL',
    'PUNCTUATOR',
    'WHITESPACE',
    'OTHER',
]


def t_IDENTIFIER(t):
    r'[_a-zA-Z][_a-zA-Z0-9]*'
    return t


def t_PREPROCESSING_NUMBER(t):
    r'\.?[0-9]([0-9]|(e\+)|(e\-)|(E\+)|(E\-)|(p\+)|(p\-)|(P\+)|(P\-)|[a-zA-Z])*'
    return t


def t_STRING_LITERAL(t):
    r"""('((\\['"tn])|[^'"\\])*')|("((\\['"tn])|[^'"\\])*")"""
    return t


def t_PUNCTUATOR(t):
    r"""[{}:;,?%&*<>=#/!]|[\[\]\(\)\.\^\-\|\+]"""
    return t


def t_WHITESPACE(t):
    r"[\t\n ]"
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

    for token in arcade:
        try:
            if token.type != 'UNKNOWN':
                print("{}: {}".format(token.type, token.value))
            else:
                print("Unknown token in input: {}".format(token.value))
                sys.exit(1)
        except:
            print('Blew up trying to access type of {}'.format(token))

    return 0


if __name__ == '__main__':
    main()
