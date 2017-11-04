#! /usr/bin/env python3
import sys
import argparse
import ply.yacc as yacc
import abstract_symbol_tree as ast
from lexer import lexer
from lexer import tokens


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


def p_error(p):
    line = 0 if p is None else p.lineno
    print("ERROR(line {}): syntax error".format(line))
    print(p)
    sys.exit(1)


# TODO: expression expansions
# TODO: cpp code expansion


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType('r'), help="The file to parse")
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
    parse_tree = parse(source, True)
    print(parse_tree)


if __name__ == "__main__":
    main()
