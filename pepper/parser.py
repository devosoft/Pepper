#! /usr/bin/env python3
import sys

import ply.yacc as yacc
import lexer
from lexer import tokens


def p_program(p):
    """
    program : statements
    """


def p_statements_empty(p):
    """
    statements:
    """


def p_statements_nonempty(p):
    """
    statements: statements statement
    """


def p_statement_rules(p):
    """
    statement   : pepper_directive
                | cpp_code
    """


def p_pepper_directive(p):
    """
    pepper_directive: # pepper_keyword expression
    """


def p_pepper_keyword(p):
    """
    pepper_keyword  : PREPROCESSING_KEYWORD_INCLUDE
                    | PREPROCESSING_KEYWORD_DEFINE
    """

# TODO: expression expansions
# TODO: cpp code expansion


def parse(source, debug_mode=False):
    if debug_mode:
        print("Entering AC parser...", file=sys.stderr)
        print("Avaliable tokens are {}".format(tokens), file=sys.stderr)
        parser = yacc.yacc(debug=True)
    else:
        parser = yacc.yacc(debug=False, errorlog=yacc.NullLogger())
    parse_tree = parser.parse(source, lexer=lexer)

    if debug_mode:
        print("Parse Successful!", file=sys.stderr)
    return parse_tree


def main():
    ilines = []
    for line in sys.stdin:
        ilines.append(line)
        # lexer.input(line)

    # terribly inefficient, but needed
    concatenated_input = "".join(ilines)

    parser = yacc.yacc(debug=True, errorlog=yacc.NullLogger)
    parse_tree = parser.parse(concatenated_input, lexer=lexer)
    print(parse_tree)
