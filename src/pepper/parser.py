#! /usr/bin/env python3
# flake8: noqa E501
import sys
import argparse
import ply.yacc as yacc
import pepper.abstract_symbol_tree as ast
from pepper.lexer import lexer
from pepper.lexer import tokens  # NOQA
import pepper.symbol_table as symtable


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
    """
    p[0] = p[1]


def p_ifdef_expression(p):
    """
    ifdef_expression : PREPROCESSING_KEYWORD_IFDEF WHITESPACE IDENTIFIER
    """
    if p[3] in symtable.TABLE.keys():
        symtable.IFDEF_STACK.append((p[3], True))
    else:
        symtable.IFDEF_STACK.append((p[3], False))

    p[0] = ast.StringLiteralNode([f"// ifdef expression {p[3]}"])


def p_ifndef_expression(p):
    """
    ifndef_expression : PREPROCESSING_KEYWORD_IFNDEF WHITESPACE IDENTIFIER
    """
    if p[3] in symtable.TABLE.keys():
        symtable.IFDEF_STACK.append((p[3], False))
    else:
        symtable.IFDEF_STACK.append((p[3], True))

    p[0] = ast.StringLiteralNode([f"// ifndef expression {p[3]}"])


def p_else_expression(p):
    """
    else_expression : PREPROCESSING_KEYWORD_ELSE
    """
    symtable.IFDEF_STACK[-1] = (symtable.IFDEF_STACK[-1][0], not symtable.IFDEF_STACK[-1][1])
    p[0] = ast.StringLiteralNode([f"// else expression "])


def p_endif_expression(p):
    """
    endif_expression : PREPROCESSING_KEYWORD_ENDIF
    """
    symtable.IFDEF_STACK.pop()
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


def p_whitespace(p):
    """
    code_expression : WHITESPACE
    """
    p[0] = ast.WhiteSpaceNode(p[1])


def p_statement_to_identifier(p):
    """
    code_expression : IDENTIFIER
    """
    p[0] = ast.IdentifierNode([p[1]])


def p_expression_to_string_lit(p):
    """
    code_expression : STRING_LITERAL
    """
    p[0] = ast.StringLiteralNode([p[1]])


def p_statement_to_ascii_literal(p):
    """
    code_expression : '<'
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
              | ':'
              | '#'
              | ','
              | '.'
    """
    p[0] = ast.ASCIILiteralNode(p[1])


def p_statement_to_preprocessing_numer(p):
    """
    code_expression : PREPROCESSING_NUMBER
    """
    p[0] = ast.PreprocessingNumberNode([p[1]])


def p_error(p):
    print(f"ERROR(line {p.lineno}): syntax error")
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
        parser = yacc.yacc(debug=True)
    else:
        parser = yacc.yacc(debug=False, errorlog=yacc.NullLogger())
    parse_tree = parser.parse(source, lexer=lexer)

    if debug_mode:
        print("Parse Successful!", file=sys.stderr)
    return parse_tree


def main():
    args = get_args()

    # source = "\n".join(args.input_file.readlines())
    parse_tree = parse(args.input_file.read(), args.debug_mode)
    print(parse_tree)


if __name__ == "__main__":
    main()
