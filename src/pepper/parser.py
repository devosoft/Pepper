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
import sys
import argparse
import ply.yacc as yacc
import pepper.abstract_symbol_tree as ast
from pepper.lexer import lexer
from pepper.lexer import tokens  # NOQA
import pepper.symbol_table as symtable

# precedence according to
# http://en.cppreference.com/w/c/language/operator_precedence

precedence = (('left', 'BOOL_OR'), ('left', 'BOOL_AND'),
              ('left', '|'),
              ('left', '^'),
              ('left', '&'),
              ('left', 'COMP_EQU', 'COMP_NEQU'),
              ('left', '<', '>', 'COMP_LTE', 'COMP_GTE'),
              ('left', 'L_SHIFT', 'R_SHIFT'),
              ('left', '+', '-'),
              ('left', '*', '/', '%'),
              ('nonassoc', '!'))

global if_count
if_count = 0
def p_program(p):
    """
    program : lines statement
    """
    p[1].children.append(p[2])
    p[0] = p[1]


def p_statements_empty(p):
    """
    lines :
    """
    p[0] = ast.LinesNode()


def p_lines_nonempty(p):
    """
    lines : lines line
    """
    statements = p[1].children + [p[2], ast.NewlineNode("\n")]
    p[0] = ast.LinesNode(statements)


def p_line_to_statement(p):
    """
    line : statement NEWLINE
    """
    p[0] = p[1]

def p_statement_to_pepper_directive(p):
    """
    statement : pepper_directive
    """
    p[0] = p[1]


def p_statement_to_code_expression(p):
    """
    statement : code_expressions
    """
    p[0] = ast.LinesNode(p[1])


def p_pepper_directive(p):
    """
    pepper_directive : preprocessor_expression
    """
    p[0] = p[1]


def p_include_expression(p):
    """
    preprocessor_expression : include_expression
                            | define_expression
                            | ifdef_expression
                            | ifndef_expression
                            | endif_expression
                            | else_expression
                            | if_expression
    """
    p[0] = p[1]

########### IF DEF EXCLUSITIVITEY

def p_valid_char(p):
    '''
    valid_expr : spaces CHAR_LITERAL spaces
    '''
    p[0] = ord(p[2][1])

def p_valid_int(p):
    '''
    valid_expr : spaces INT_LITERAL spaces
    '''
    p[0] = int(p[2])


def p_valid_macro(p):
    '''
    valid_expr : spaces IDENTIFIER spaces
    '''
    val = symtable.TABLE.get(p[2], 0)
    if isinstance(val , symtable.MacroExpansion):

            # add error checking for floats
        val = int(val.expansion) if val.expansion.isdigit() else 0

    p[0] = val


def p_valid_add(p):
    '''
    valid_expr : valid_expr '+' valid_expr
    '''

    p[0] = p[1] + p[3]

def p_valid_sub(p):
    '''
    valid_expr : valid_expr '-' valid_expr
    '''

    p[0] = p[1] - p[3]

def p_valid_mult(p):
    '''
    valid_expr : valid_expr '*' valid_expr
    '''

    p[0] = p[1] * p[3]

def p_valid_div(p):
    '''
    valid_expr : valid_expr '/' valid_expr
    '''

    p[0] = p[1] / p[3]

def p_valid_mod(p):
    '''
    valid_expr : valid_expr '%' valid_expr
    '''

    p[0] = p[1] % p[3]

def p_valid_bit_not(p):
    '''
    valid_expr : '~' valid_expr
    '''
    p[0] = ~p[2]

def p_valid_bit_or(p):
    '''
    valid_expr : valid_expr '|' valid_expr
    '''

    p[0] = p[1] | p[3]

def p_valid_bit_and(p):
    '''
    valid_expr : valid_expr '&' valid_expr
    '''

    p[0] = p[1] & p[3]

def p_valid_bit_xor(p):
    '''
    valid_expr : valid_expr '^' valid_expr
    '''

    p[0] = p[1] ^ p[3]

def p_valid_bit_lshift(p):
    '''
    valid_expr : valid_expr L_SHIFT valid_expr
    '''

    p[0] = p[1] << p[3]

def p_valid_bit_rshift(p):
    '''
    valid_expr : valid_expr R_SHIFT valid_expr
    '''

    p[0] = p[1] >> p[3]

def p_valid_logic_or(p):
    '''
    valid_expr : valid_expr BOOL_OR valid_expr
    '''

    p[0] = (p[1] or p[3]) == True

def p_valid_logic_and(p):
    '''
    valid_expr : valid_expr BOOL_AND valid_expr
    '''

    p[0] = (p[1] and p[3]) == True

def p_valid_logic_not(p):
    '''
    valid_expr : '!' valid_expr
    '''

    p[0] = (not p[2] ) == True

def p_valid_logic_lt(p):
    '''
    valid_expr : valid_expr '<' valid_expr
    '''
    p[0] = p[1] < p[3]

def p_valid_logic_le(p):
    '''
    valid_expr : valid_expr COMP_LTE valid_expr
    '''
    p[0] = p[1] <= p[3]

def p_valid_logic_gt(p):
    '''
    valid_expr : valid_expr '>' valid_expr
    '''
    p[0] = p[1] > p[3]

def p_valid_logic_ge(p):
    '''
    valid_expr : valid_expr COMP_GTE valid_expr
    '''
    p[0] = p[1] >= p[3]

def p_valid_equal(p):
    '''
    valid_expr : valid_expr COMP_EQU valid_expr
    '''
    p[0] = p[1]  == p[3]

def p_valid_nequal(p):
    '''
    valid_expr : valid_expr COMP_NEQU valid_expr
    '''
    p[0] = p[1] != p[3]

#TODO: support parenthesis
def p_if_expression(p):
    """
    if_expression : PREPROCESSING_KEYWORD_IF WHITESPACE valid_expr
    """
    global if_count
    if_count += 1
    symtable.IF_STACK.append((if_count, p[3]))
    p[0] = ast.StringLiteralNode([f"// if expression {if_count } "])

    #if p[3] == 'defined':
    #    symtable.IF_STACK.append((p[5], p[5] in symtable.TABLE.keys()))
    #    p[0] = ast.StringLiteralNode([f"// if expression w/ defined call {p[5]}"])
    #else:
    #    pass
    # figure out best way to error calls that arent 'defined' put in lexer?



def p_no_space(p):
    '''
    spaces :
    '''

    p[0] = None

def p_spaces(p):
    '''
    spaces : WHITESPACE spaces
    '''

    p[0] = ast.WhiteSpaceNode([p[1]])

####### DONE

def p_ifdef_expression(p):
    """
    ifdef_expression : PREPROCESSING_KEYWORD_IFDEF WHITESPACE IDENTIFIER
    """
    symtable.IF_STACK.append((p[3], p[3] in symtable.TABLE.keys()))

    p[0] = ast.StringLiteralNode([f"// ifdef expression {p[3]}"])




def p_ifndef_expression(p):
    """
    ifndef_expression : PREPROCESSING_KEYWORD_IFNDEF WHITESPACE IDENTIFIER
    """
    symtable.IF_STACK.append((p[3], p[3] not in symtable.TABLE.keys()))

    p[0] = ast.StringLiteralNode([f"// ifndef expression {p[3]}"])


def p_else_expression(p):
    """
    else_expression : PREPROCESSING_KEYWORD_ELSE
    """
    symtable.IF_STACK[-1] = (symtable.IF_STACK[-1][0], not symtable.IF_STACK[-1][1])
    p[0] = ast.StringLiteralNode([f"// else expression "])


def p_endif_expression(p):
    """
    endif_expression : PREPROCESSING_KEYWORD_ENDIF
    """
    symtable.IF_STACK.pop()
    p[0] = ast.StringLiteralNode([f"// endif expression "])


def p_define_expression_no_expansion(p):
    """
    define_expression : PREPROCESSING_KEYWORD_DEFINE WHITESPACE IDENTIFIER
    """
    p[0] = symtable.MacroExpansion(p[3], [ast.IdentifierNode(["true"])])


def p_define_expression_no_args(p):
    """
    define_expression : PREPROCESSING_KEYWORD_DEFINE WHITESPACE IDENTIFIER WHITESPACE macro_expansion
    """
    p[0] = symtable.MacroExpansion(p[3], p[5])


def p_define_expression_some_args(p):
    """
    define_expression : PREPROCESSING_KEYWORD_DEFINE WHITESPACE IDENTIFIER '(' identifier_list ')'  WHITESPACE macro_expansion
    """
    print(f"Macro expansion for ident {p[3]} with args {p[5]}")
    p[0] = symtable.MacroExpansion(p[3], p[8], args=p[5])


def p_identifier_list_singleton(p):
    """
    identifier_list : IDENTIFIER
    """
    p[0] = [p[1]]


def p_identifier_list_empty(p):
    """
    identifier_list :
    """
    p[0] = []


def p_identifier_list_multiple(p):
    """
    identifier_list : identifier_list ',' maybe_space IDENTIFIER
    """
    p[0] = p[1]
    p[0].append(p[4])


def p_maybe_whitespace_none(p):
    """
    maybe_space :
    """
    p[0] = ast.WhiteSpaceNode([""])


def p_maybe_whitespace_some(p):
    """
    maybe_space : WHITESPACE
    """
    p[0] = ast.WhiteSpaceNode([p[1]])


def p_include_expression_disambiguation(p):
    """
    include_expression : include_expression_file
                       | include_expression_system
    """
    p[0] = p[1]


def p_define_expansion(p):
    """
    macro_expansion : code_expressions
    """
    p[0] = p[1]


def p_include_expression_file(p):
    """
    include_expression_file : PREPROCESSING_KEYWORD_INCLUDE WHITESPACE STRING_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], False)


def p_include_expression_system(p):
    """
    include_expression_system : PREPROCESSING_KEYWORD_INCLUDE WHITESPACE SYSTEM_INCLUDE_LITERAL
    """
    p[0] = ast.PreprocessorIncludeNode([p[3]], True)


def p_expressions_empty(p):
    """
    code_expressions :
    """
    p[0] = []


def p_expressions(p):
    """
    code_expressions : code_expressions code_expression
    """
    p[0] = p[1]
    p[0].append(p[2])


def p_identifier_call(p):
    """
    safe_code_expression : IDENTIFIER code_expression_parenthetical
    """
    print(f"macro call with ident {p[1]} and args {p[2]}")
    p[0] = ast.IdentifierNode([p[1]], args=p[2])


def p_code_expression_to_safe(p):
    """
    code_expression : safe_code_expression
    """
    p[0] = p[1]


def p_statement_to_identifier(p):
    """
    safe_code_expression : IDENTIFIER
    """
    p[0] = ast.IdentifierNode([p[1]])


def p_expression_to_list_of_something(p):
    """
    code_expression_parenthetical : '(' list_of_expressions ')'
    """
    p[0] = p[2]


def p_whitespace_unsafe(p):
    """
    safe_code_expression : WHITESPACE
    """
    p[0] = ast.WhiteSpaceNode([p[1]])


def p_expression_to_string_lit(p):
    """
    safe_code_expression : STRING_LITERAL
    """
    p[0] = ast.StringLiteralNode([p[1]])



def p_expression_list_singleton(p):
    """
    list_of_expressions : safe_code_expressions
    """
    p[0] = [ast.LinesNode(p[1])]


def p_expression_list_empty(p):
    """
    list_of_expressions :
    """
    p[0] = []


def p_expression_list_multiple(p):
    """
    list_of_expressions : list_of_expressions ',' maybe_space safe_code_expressions
    """
    p[0] = p[1]
    p[0].append(ast.LinesNode(p[4]))


# don't  mind me, just duplicating code...ugh
def p_safe_expressions_empty(p):
    """
    safe_code_expressions :
    """
    p[0] = []


def p_safe_expressions(p):
    """
    safe_code_expressions : safe_code_expressions safe_code_expression
    """
    p[0] = p[1]
    p[0].append(p[2])


def p_safe_code_expressions_ascii_literal(p):
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
    """
    p[0] = ast.ASCIILiteralNode(p[1])


def p_statement_to_ascii_literal(p):
    """
    code_expression :
              | ','
              | '('
              | ')'
    """
    p[0] = ast.ASCIILiteralNode(p[1])


def p_statement_to_preprocessing_number(p):
    """
    safe_code_expression : PREPROCESSING_NUMBER
    """
    p[0] = ast.PreprocessingNumberNode([p[1]])

def p_statement_to_int(p):
    """
    safe_code_expression : INT_LITERAL
    """
    p[0] = ast.PreprocessingNumberNode([p[1]])

def p_error(p):
    print(f"ERROR(line {p.lineno}): syntax error")
    print(p)
    raise symtable.PepperSyntaxError()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=argparse.FileType('r'), help="The file to parse")
    parser.add_argument('--debug_mode', action='store_true')
    return parser.parse_args()


def parse(source, debug_mode=False):
    if debug_mode:
        parser = yacc.yacc(debug=True)
    else:
        parser = yacc.yacc(debug=False, errorlog=yacc.NullLogger())
    parse_tree = parser.parse(source, lexer=lexer)

    return parse_tree


def main():
    args = get_args()

    # source = "\n".join(args.input_file.readlines())
    parse_tree = parse(args.input_file.read(), args.debug_mode)
    print(parse_tree)


if __name__ == "__main__":
    main()
