#! /usr/bin/env python3

# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This is the Parser module for Pepper

This module impelements the grammar for the preprocessor language, comprised of tokens from the Lexer module.
This module implements a main function, but this is only for debugging and will be removed on release.
"""

# flake8: noqa E501
import pepper.symbol_table as symtable
import pepper.abstract_symbol_tree as ast
import sys
import argparse
import ply.yacc as yacc
from pepper.lexer import lexer
from pepper.lexer import tokens  # NOQA
from pepper.symbol_table import Node


def p_program(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    program : lines statement
    """
    p[1].children.append(p[2])
    p[0] = p[1]


def p_statements_empty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    lines :
    """
    p[0] = ast.LinesNode()


def p_lines_nonempty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    lines : lines line
    """
    statements = p[1].children + [p[2], ast.NewlineNode(["\n"])]
    p[0] = ast.LinesNode(statements)


def p_line_to_statement(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    line : statement NEWLINE
    """
    p[0] = p[1]


def p_statement_to_pepper_directive(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    statement : pepper_directive
    """
    p[0] = p[1]


def p_statement_to_code_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    statement : code_expressions
    """
    p[0] = ast.LinesNode(p[1])


def p_pepper_directive(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    pepper_directive : preprocessor_expression
    """
    p[0] = p[1]


def p_include_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    preprocessor_expression : include_expression
                            | define_expression
                            | ifdef_expression
                            | ifndef_expression
                            | endif_expression
                            | else_expression
    """
    p[0] = p[1]


def p_ifdef_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    ifdef_expression : PREPROCESSING_KEYWORD_IFDEF WHITESPACE IDENTIFIER
    """
    if p[3] in symtable.TABLE.keys():
        symtable.IFDEF_STACK.append((p[3], True))
    else:
        symtable.IFDEF_STACK.append((p[3], False))

    p[0] = ast.StringLiteralNode([f"// ifdef expression {p[3]}"])


def p_ifndef_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    ifndef_expression : PREPROCESSING_KEYWORD_IFNDEF WHITESPACE IDENTIFIER
    """
    if p[3] in symtable.TABLE.keys():
        symtable.IFDEF_STACK.append((p[3], False))
    else:
        symtable.IFDEF_STACK.append((p[3], True))

    p[0] = ast.StringLiteralNode([f"// ifndef expression {p[3]}"])


def p_else_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    else_expression : PREPROCESSING_KEYWORD_ELSE
    """
    symtable.IFDEF_STACK[-1] = (symtable.IFDEF_STACK[-1][0], not symtable.IFDEF_STACK[-1][1])
    p[0] = ast.StringLiteralNode([f"// else expression "])


def p_endif_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    endif_expression : PREPROCESSING_KEYWORD_ENDIF
    """
    symtable.IFDEF_STACK.pop()
    p[0] = ast.StringLiteralNode([f"// endif expression "])


def p_define_expression_no_expansion(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    define_expression : PREPROCESSING_KEYWORD_DEFINE WHITESPACE IDENTIFIER
    """
    p[0] = symtable.MacroExpansion(p[3], [ast.IdentifierNode(["true"])])


def p_define_expression_no_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    define_expression : PREPROCESSING_KEYWORD_DEFINE WHITESPACE IDENTIFIER WHITESPACE macro_expansion
    """
    p[0] = symtable.MacroExpansion(p[3], p[5])


def p_define_expression_some_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    define_expression : PREPROCESSING_KEYWORD_DEFINE WHITESPACE IDENTIFIER '(' identifier_list ')'  maybe_space macro_expansion
    """
    print(f"Macro expansion for ident {p[3]} with args {p[5]}")
    p[0] = symtable.MacroExpansion(p[3], p[8], args=p[5])


def p_identifier_list_singleton(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    identifier_list : IDENTIFIER
    """
    p[0] = [p[1]]


def p_identifier_list_empty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    identifier_list :
    """
    p[0] = []


def p_identifier_list_multiple(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    identifier_list : identifier_list ',' maybe_space IDENTIFIER
    """
    p[0] = p[1]
    p[0].append(p[4])


def p_maybe_whitespace_none(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    maybe_space :
    """
    p[0] = ast.WhiteSpaceNode([""])


def p_maybe_whitespace_some(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    maybe_space : WHITESPACE
    """
    p[0] = ast.WhiteSpaceNode([p[1]])


def p_include_expression_disambiguation(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    include_expression : include_expression_file
                       | include_expression_system
    """
    p[0] = p[1]


def p_define_expansion(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    macro_expansion : code_expressions
    """
    p[0] = p[1]


def p_include_expression_file(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    include_expression_file : PREPROCESSING_KEYWORD_INCLUDE WHITESPACE STRING_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], False)


def p_include_expression_system(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    include_expression_system : PREPROCESSING_KEYWORD_INCLUDE WHITESPACE SYSTEM_INCLUDE_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], True)


def p_expressions_empty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    code_expressions :
    """
    p[0] = []


def p_expressions(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    code_expressions : code_expressions code_expression
    """
    p[0] = p[1]
    p[0].append(p[2])


def p_expressions_to_single(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    code_expressions : code_expression
    """
    p[0] = [p[1]]


def p_identifier_call(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : IDENTIFIER code_expression_parenthetical
    """
    print(f"macro call with ident {p[1]} and args {p[2]}")
    p[0] = ast.IdentifierNode([p[1]], args=p[2])


def p_safe_code_expression_to_parens(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : code_expression_parenthetical
    """
    p[0] = ast.LinesNode([ast.ASCIILiteralNode(['(']),
                          ast.LinesNode(p[1]),
                          ast.ASCIILiteralNode([')'])
                         ])


def p_code_expression_to_safe(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    code_expression : safe_code_expression
    """
    p[0] = p[1]


def p_statement_to_identifier(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : IDENTIFIER
    """
    p[0] = ast.IdentifierNode([p[1]])


def p_expression_to_list_of_something(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    code_expression_parenthetical : '(' list_of_expressions ')'
    """
    p[0] = p[2]


def p_whitespace_unsafe(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : WHITESPACE
    """
    p[0] = ast.WhiteSpaceNode([p[1]])


def p_expression_to_string_lit(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : STRING_LITERAL
    """
    p[0] = ast.StringLiteralNode([p[1]])



def p_expression_list_singleton(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    list_of_expressions : safe_code_expressions
    """
    p[0] = [ast.LinesNode(p[1])]


def p_expression_list_empty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    list_of_expressions :
    """
    p[0] = []


def p_expression_list_multiple(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    list_of_expressions : list_of_expressions ',' safe_code_expressions
    """
    p[0] = p[1]
    p[0].append(ast.LinesNode(p[3]))


# don't  mind me, just duplicating code...ugh
def p_safe_expressions_empty(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expressions :
    """
    p[0] = []


def p_safe_expressions(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expressions : safe_code_expressions safe_code_expression
    """
    p[0] = p[1]
    p[0].append(p[2])


def p_safe_code_expressions_ascii_literal(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : '<'
              | '>'
              | '+'
              | '-'
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
              | ':'
              | '#'
              | '.'
              | '?'
              | '~'
    """
    p[0] = ast.ASCIILiteralNode(p[1])


def p_statement_to_ascii_literal(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    code_expression :
              | ','
              | '('
              | ')'
    """
    p[0] = ast.ASCIILiteralNode(p[1])


def p_statement_to_preprocessing_number(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : PREPROCESSING_NUMBER
    """
    p[0] = ast.PreprocessingNumberNode([p[1]])


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
