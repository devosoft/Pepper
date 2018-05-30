#! /usr/bin/env python3

# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This is the Parser module for Pepper

This module implements the grammar for the preprocessor language, comprised of tokens from the Lexer module.
This module implements a main function, but this is only for debugging and will be removed on release.
"""

# flake8: noqa E501
import pepper.symbol_table as symtable
import pepper.abstract_symbol_tree as ast
import sys
import argparse
import ply.yacc as yacc
from pepper.preprocessor_language_lexer import lexer
from pepper.preprocessor_language_lexer import tokens  # NOQA
import pepper.symbol_table as symtable
from pepper.evaluator import parse_lines, parse_macro
from pepper.symbol_table import Node
from typing import List, cast


print(f"tokens: {tokens}")


def p_statement(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    program : '#' preprocessing_statement NEWLINE
    """
    pass


def p_preprocessing_statement_to_all_statement_types(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    preprocessing_statement : define_statement
                            | include_statement
    """
    pass


def p_define_statement_structure(p: yacc.YaccProduction) -> yacc.YaccProduction:
    pass


def p_define_expression_no_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    define_statement : PREPROCESSING_KEYWORD_DEFINE maybe_space IDENTIFIER maybe_space expressions
    """
    # p[0] = symtable.MacroExpansion(p[3], p[5])
    pass


# def p_define_expression_some_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
#     """
#     define_expression : PREPROCESSING_KEYWORD_DEFINE maybe_space IDENTIFIER '(' identifier_list ')'  maybe_space expressions
#     """
#     # print(f"Macro expansion for ident {p[3]} with args {p[5]}")
#     # p[0] = symtable.MacroExpansion(p[3], p[8], args=p[5])
#     pass


def p_include_expression_disambiguation(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    include_statement : include_statement_file
                       | include_statement_system
    """
    p[0] = p[1]


def p_include_expression_file(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    include_statement_file : PREPROCESSING_KEYWORD_INCLUDE maybe_space STRING_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], False)


def p_include_expression_system(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    include_statement_system : PREPROCESSING_KEYWORD_INCLUDE maybe_space SYSTEM_INCLUDE_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], True)


def p_maybe_space_empty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    maybe_space :
    """
    pass


def p_maybe_space_nonempty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    maybe_space : WHITESPACE
    """
    pass


def p_expressions(p):
    """
    expressions : IDENTIFIER
    """
    pass


def p_error(p: yacc.YaccProduction) -> yacc.YaccProduction:
    print(f"ERROR(line {p.lineno}): syntax error")
    print(p)
    raise symtable.PepperSyntaxError()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help="The file to parse")
    parser.add_argument('--debug_mode', action='store_true')
    return parser.parse_args()


def parse(source: str, debug_mode: bool=False) -> Node:
    if debug_mode:
        parser = yacc.yacc(debug=True)
    else:
        parser = yacc.yacc(debug=False, errorlog=yacc.NullLogger())
    parse_tree: Node = parser.parse(source, lexer=lexer)

    return parse_tree


def main() -> None:
    args = get_args()

    # source = "\n".join(args.input_file.readlines())
    parse_tree = parse(args.input_file.read(), args.debug_mode)
    print(parse_tree)


if __name__ == "__main__":
    main()