#! /usr/bin/env python3
import sys
import argparse
import ply.yacc as yacc
import pepper.abstract_symbol_tree as ast
from pepper.lexer import lexer
from pepper.lexer import tokens  # NOQA


def p_program(p):
    """
    program : statements
    """
    p[0] = p[1]


def p_statements_empty(p):
    """
    statements :
    """
    p[0] = ast.StatementsNode()


def p_statements_nonempty(p):
    """
    statements : statements statement
    """
    statements = p[1].children + [p[2]]
    p[0] = ast.StatementsNode(statements)


def p_statement_rules(p):
    """
    statement   : pepper_directive
    """
    p[0] = p[1]


def p_pepper_directive(p):
    """
    pepper_directive : preprocessor_expression
    """
    p[0] = p[1]


def p_expression(p):
    """
    preprocessor_expression : include_expression
    """
    p[0] = p[1]


def p_include_expression_file(p):
    """
    include_expression : '#' PREPROCESSING_KEYWORD_INCLUDE STRING_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], False)


def p_include_expression_system(p):
    """
    include_expression : '#' PREPROCESSING_KEYWORD_INCLUDE '<' IDENTIFIER '>'
    """
    p[0] = ast.PreprocessorIncludeNode([p[4]], True)


# def p_identifier_with_parentheses(p):
#     """
#     """


def p_statement_to_identifier(p):
    """
    statement : IDENTIFIER
    """
    p[0] = ast.IdentifierNode([p[1]])


def p_statement_to_ascii_literal(p):
    """
    statement : '<'
              | '>'
              | '+'
              | '-'
              | '('
              | ')'
              | '%'
              | '^'
              | '&'
              | '*'
              | '{'
              | '}'
              | '['
              | ']'
              | '='
              | ';'
    """
    p[0] = p[1]


def p_statement_to_preprocessing_numer(p):
    """
    statement : PREPROCESSING_NUMBER
    """
    p[0] = ast.PreprocssingNumberNode([p[1]])


def p_error(p):
    line = 0 if p is None else p.lineno
    print("ERROR(line {}): syntax error".format(line))
    print(p)
    raise Exception


# TODO: expression expansions
# TODO: cpp code expansion


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType('r'), help="The file to parse")
    parser.add_argument('--debug_mode', action='store_true')
    return parser.parse_args()


def parse(source, debug_mode=False):
    if debug_mode:
        # print("Entering AC parser...", file=sys.stderr)
        # print("Avaliable tokens are {}".format(tokens), file=sys.stderr)
        parser = yacc.yacc(debug=True)
    else:
        parser = yacc.yacc(debug=False, errorlog=yacc.NullLogger())
    parse_tree = parser.parse(source, lexer=lexer)

    if debug_mode:
        print("Parse Successful!", file=sys.stderr)
    return parse_tree


def main():
    args = get_args()

    source = "\n".join(args.input_file.readlines())
    parse_tree = parse(source, args.debug_mode)
    print(parse_tree)


if __name__ == "__main__":
    main()
