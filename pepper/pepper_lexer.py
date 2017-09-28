#! /usr/bin/env python3
import sys
import ply.lex as lex

tokens = [
    'PREPROCESSOR_DIRECTIVE',
    'COMMENT',
    'NEWLINE',
    'CODE',
]


def t_PREPROCESSOR_DIRECTIVE(t):
    r'\#.*'
    return t


def t_COMMENT(t):
    r'\//.*|/\*.*\*/'
    return t


def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_WHITESPACE(t):
    r'[ \t]+'
    #return t
    pass


def t_CODE(t):
    r'.+'
    return t


def t_error(t):
    print("Unknown token on line {}: {}".format(t.lexer.lineno, t.value[0]))
    exit(1)

lexer = lex.lex()

def main():
    ilines = []
    for line in sys.stdin:
        ilines.append(line)
        #lexer.input(line)

    # terribly inefficient, but we needed
    lexer.input("".join(ilines))

    arcade = []
    tok = True
    while True:
        tok = lexer.token()
        if not tok:
            break  # end of file reached
        arcade.append(tok)


    ignore = ['COMMENT', 'WHITESPACE']

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
