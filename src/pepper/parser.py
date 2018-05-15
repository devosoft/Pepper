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
from pepper.lexer import lexer
from pepper.lexer import tokens  # NOQA
import pepper.symbol_table as symtable
from pepper.evaluator import parse_lines, parse_macro
from pepper.symbol_table import Node
from typing import List, cast

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
              ('right', '!', '~'))


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
                     | error_directive
                     | warning_directive
    """
    p[0] = p[1]


def p_include_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    preprocessor_expression : include_expression
                            | define_expression
                            | else_expression
                            | endif_expression
                            | if_expression
                            | ifdef_expression
                            | ifndef_expression
                            | pragma_expression
    """
    p[0] = p[1]


########### IF DEF EXCLUSITIVITEY
def p_valid_char(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces CHAR_LITERAL spaces
    '''
    p[0] = ord(p[2][1])


def p_valid_int(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces INT_LITERAL spaces
    '''
    p[0] = int(p[2])


def p_valid_macro(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces IDENTIFIER spaces
    '''
    val = symtable.TABLE.get(p[2], 0)
    if isinstance(val , symtable.MacroExpansion):
        val = parse_macro(val.tokens)
    p[0] = val


def p_valid_defined(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces DEFINED spaces '(' spaces IDENTIFIER spaces ')' spaces
    '''

    p[0] =  p[6] in symtable.TABLE


def p_valid_defined_no_paren(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces DEFINED spaces IDENTIFIER spaces
    '''

    p[0] =  p[4] in symtable.TABLE


def p_valid_macro_no_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces IDENTIFIER spaces '(' spaces ')' spaces
    '''
    val = symtable.TABLE.get(p[2], 0)
    if isinstance(val , symtable.MacroExpansion):
        val.expand()
        val = parse_macro(val.tokens)
        symtable.EXPANDED_MACRO = False
    p[0] = val


def p_valid_macro_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces IDENTIFIER spaces valid_args spaces
    '''
    val = symtable.TABLE.get(p[2], 0)
    arg_tokens = p[4][:]
    args = [child.children[0] for child in p[4]]

    if isinstance(val , symtable.MacroExpansion):
        # error check argument count
        expansion = val.expand(args)

        old_tokens: List[object] = [parse_lines(val.tokens[i]) if isinstance(val.tokens[i], ast.LinesNode) else
                                    val.tokens[i] for i in range(len(val.tokens)) ]
        new_tokens = []
        while old_tokens:
            token = old_tokens.pop(0)
            while isinstance(token, list):
                old_tokens = token + old_tokens
                token = old_tokens.pop(0)
            if isinstance(token ,ast.IdentifierNode):
                if val.args:
                    if token.children[0] in val.args:
                        index = val.args.index(cast(str, token.children[0]))
                        token = arg_tokens[index]


            new_tokens.append(token)

        val = parse_macro(cast(List['Node'],new_tokens))
        symtable.EXPANDED_MACRO = False


    p[0] = val


def p_valid_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_args : '(' spaces valid_arg spaces  ')'
    '''
    p[0] = p[3]


def p_valid_arg(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_arg :  valid_expr
    '''
    p[0]  = [ast.PreprocessingNumberNode([str(int(p[1]))])]


def p_valid_arg_commas(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_arg : valid_arg spaces ',' spaces valid_arg spaces
    '''

    p[0] = p[1] + p[5]


def p_valid_parentheticals(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces '(' spaces valid_expr spaces ')' spaces
    '''
    p[0] = p[4]


def p_valid_add(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '+' valid_expr
    '''

    p[0] = p[1] + p[3]


def p_valid_sub(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '-' valid_expr
    '''

    p[0] = p[1] - p[3]


def p_valid_mult(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '*' valid_expr
    '''

    p[0] = p[1] * p[3]


def p_valid_div(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '/' valid_expr
    '''

    p[0] = p[1] // p[3]


def p_valid_mod(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '%' valid_expr
    '''

    p[0] = p[1] % p[3]


def p_valid_bit_not(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : '~' valid_expr
    '''
    p[0] = ~p[2]


def p_valid_bit_or(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '|' valid_expr
    '''

    p[0] = p[1] | p[3]


def p_valid_bit_and(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '&' valid_expr
    '''

    p[0] = p[1] & p[3]


def p_valid_bit_xor(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '^' valid_expr
    '''

    p[0] = p[1] ^ p[3]


def p_valid_bit_lshift(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr L_SHIFT valid_expr
    '''

    p[0] = p[1] << p[3]


def p_valid_bit_rshift(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr R_SHIFT valid_expr
    '''

    p[0] = p[1] >> p[3]


def p_valid_logic_or(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr BOOL_OR valid_expr
    '''

    p[0] = bool(p[1] or p[3])


def p_valid_logic_and(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr BOOL_AND valid_expr
    '''

    p[0] = bool(p[1] and p[3])


def p_valid_logic_not(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : spaces '!' spaces valid_expr
    '''

    p[0] = (not p[4] ) == True


def p_valid_logic_lt(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '<' valid_expr
    '''
    p[0] = p[1] < p[3]


def p_valid_logic_le(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr COMP_LTE valid_expr
    '''
    p[0] = p[1] <= p[3]


def p_valid_logic_gt(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr '>' valid_expr
    '''
    p[0] = p[1] > p[3]


def p_valid_logic_ge(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr COMP_GTE valid_expr
    '''
    p[0] = p[1] >= p[3]


def p_valid_equal(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr COMP_EQU valid_expr
    '''
    p[0] = p[1]  == p[3]


def p_valid_nequal(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr COMP_NEQU valid_expr
    '''
    p[0] = p[1] != p[3]


def p_valid_ternary(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    valid_expr : valid_expr spaces '?' spaces valid_expr ':' valid_expr
    '''
    p[0] = p[5] if p[1] else p[7]


def p_if_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    if_expression : PREPROCESSING_KEYWORD_IF WHITESPACE valid_expr
    """
    symtable.IF_COUNT += 1

    symtable.IF_STACK.append((str(symtable.IF_COUNT), p[3]))
    p[0] = ast.StringLiteralNode([f"// if expression result: { int(p[3]) }"])


def p_no_space(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    spaces :
    '''

    p[0] = None


def p_spaces(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    spaces : WHITESPACE spaces
    '''

    p[0] = ast.WhiteSpaceNode([p[1]])

# TODO: make nodes instead that have the appropriate children and evaluated expression?
####### DONE


def p_ifdef_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    ifdef_expression : PREPROCESSING_KEYWORD_IFDEF WHITESPACE IDENTIFIER
    """
    symtable.IF_STACK.append((p[3], p[3] in symtable.TABLE))

    p[0] = ast.StringLiteralNode([f"// ifdef expression {p[3]}"])


def p_ifndef_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    ifndef_expression : PREPROCESSING_KEYWORD_IFNDEF WHITESPACE IDENTIFIER
    """
    symtable.IF_STACK.append((p[3], p[3] not in symtable.TABLE))

    p[0] = ast.StringLiteralNode([f"// ifndef expression {p[3]}"])


def p_pragma(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    pragma_expression : PREPROCESSING_KEYWORD_PRAGMA WHITESPACE IDENTIFIER WHITESPACE macro_expansion
    """
    p[0] = ast.PragmaHandlerNode([p[3], p[5]])


def p_pragma_no_args(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    pragma_expression : PREPROCESSING_KEYWORD_PRAGMA WHITESPACE IDENTIFIER
    """
    p[0] = ast.PragmaHandlerNode([p[3]])


def p_else_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    else_expression : PREPROCESSING_KEYWORD_ELSE
    """
    symtable.IF_STACK[-1] = (symtable.IF_STACK[-1][0], not symtable.IF_STACK[-1][1])
    p[0] = ast.StringLiteralNode([f"// else expression "])


def p_endif_expression(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    endif_expression : PREPROCESSING_KEYWORD_ENDIF
    """
    symtable.IF_STACK.pop()
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
              | '/'
    """
    p[0] = ast.ASCIILiteralNode(p[1])


# distinction is ascii literals to preprocessor issues (2 character operators)
def p_safe_code_expression_operator(p: yacc.YaccProduction) -> yacc.YaccProduction:
    '''
    safe_code_expression : COMP_LTE
                        |   COMP_GTE
                        |   COMP_EQU
                        |   COMP_NEQU
                        |   BOOL_AND
                        |   BOOL_OR
                        |   L_SHIFT
                        |   R_SHIFT
    '''

    p[0] = ast.OperatorNode([p[1]])


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


def p_statement_to_int(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : INT_LITERAL
    """
    p[0] = ast.PreprocessingNumberNode([p[1]])


def p_statement_to_char(p: yacc.YaccProduction) -> yacc.YaccProduction:
    """
    safe_code_expression : CHAR_LITERAL
    """
    p[0] = ast.StringLiteralNode([p[1]])


def p_error_directive(p: yacc.YaccProduction) ->yacc.YaccProduction:
    """
    error_directive : PREPROCESSING_KEYWORD_ERROR spaces STRING_LITERAL
    """
    p[0] = ast.PreprocessorErrorNode( [p[3]], symtable.LINE_COUNT, symtable.FILE_STACK[-1].name)


def p_warning_directive(p: yacc.YaccProduction) ->yacc.YaccProduction:
    """
    warning_directive : PREPROCESSING_KEYWORD_WARNING spaces STRING_LITERAL
    """
    p[0] = ast.PreprocessorWarningNode([p[3]], symtable.LINE_COUNT, symtable.FILE_STACK[-1].name)


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