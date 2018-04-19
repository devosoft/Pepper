#! /usr/bin/env python3

# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This is the evaluator module for Pepper

This evaluator is specific to parsing and evaluating macro calls within the if directive.
This should not be used in isolation.
"""

import pepper.abstract_symbol_tree as ast
import pepper.symbol_table as symtable
from typing import Union, List, cast
from pepper.symbol_table import Node  # NOQA

Child = Union[str, Node]


def validate(exp: Node) -> str:
    literal = ""
    if isinstance(exp, ast.PreprocessingNumberNode) or \
            isinstance(exp, ast.ASCIILiteralNode) or isinstance(exp, ast.OperatorNode):
        if isinstance(exp.children[0], str):
            literal = exp.children[0]
            if literal == '&&':
                literal = 'and'
            elif literal == '||':
                literal = 'or'

    elif isinstance(exp, ast.StringLiteralNode):
        if isinstance(exp.children[0], str):
            literal = str(ord(exp.children[0][1]))

    return literal


def parse_line(t: List[Child]) -> List[Child]:
    if isinstance(t[0], ast.LinesNode):

        return parse_lines(t[0])
    # while isinstance(t[0], ast.IdentifierNode):
    #    if t[0].children[0] in symtable.TABLE:
    #        t = symtable.TABLE[t[0].children[0]].tokens
    #    else:
    #        t = [0]

    return t


def parse_lines(token: Node) -> List[Child]:
    temp = []
    for t in token.children:
        tok = parse_line([t])
        temp.extend(tok)

    return temp


def unravel_list(exp: Union[List[List[Node]], List[Node], Node])-> List[Node]:
    parsing: List['Node'] = []
    if isinstance(exp, list):
        for tok in exp:
            while isinstance(tok, list):
                temp = tok.pop(0)
                if not tok and not isinstance(temp, list):
                    tok = temp
                elif not tok:
                    parsing.append(ast.ASCIILiteralNode(['(']))
                    tok = temp
                    parsing.append(ast.ASCIILiteralNode([')']))
                else:
                    parsing.append(ast.ASCIILiteralNode(['(']))
                    parsing.extend(unravel_list(temp))
                    parsing.append(ast.ASCIILiteralNode([')']))

            parsing.append(tok)

    i = 0
    while i + 2 < len(parsing):
        found = False
        if isinstance(parsing[i], ast.ASCIILiteralNode) \
                and isinstance(parsing[i+1], ast.WhiteSpaceNode) \
                and isinstance(parsing[i+2], ast.ASCIILiteralNode):
            parsing.pop(i)
            parsing.pop(i)
            parsing.pop(i)
            found = True
        if not found:
            i += 1

    return parsing


def convert_nodes_to_expr(scalar_tokens: List[List['Node']]) -> List[str]:
    evaluation = []

    for expr in scalar_tokens:
        for exp in expr:
            if isinstance(exp, list):
                exp = unravel_list(exp)
                temp = [validate(t) for t in exp if not isinstance(t, ast.WhiteSpaceNode)
                        and isinstance(t, Node)]
                evaluation.extend(temp)
            elif not isinstance(exp, ast.WhiteSpaceNode):
                evaluation.append(validate(exp))

    clean_parathensis(evaluation)
    evaluation = convert_to_python(evaluation)

    return evaluation


def clean_parathensis(evaluation: List[str]) -> None:
    OPERATORS = {'+', '-', '*', '/', 'and', 'or', '&', '|', '<<', '>>', '^'}
    i = 0

    while i + 1 < len(evaluation):
        found = False
        if evaluation[i] == "(" and evaluation[i+1] == ")":
            evaluation.pop(i)
            evaluation.pop(i)
            found = True
        if not found:
            i += 1

    i = 0
    while i + 2 < len(evaluation):
        found = False
        if evaluation[i] == '(' and evaluation[i+1] in OPERATORS and evaluation[i+2] == ')':
            evaluation.pop(i)
            evaluation.pop(i+1)
        i += 1


def convert_to_python(evaluation: List[str]) -> List[str]:
    # catch AND && OR stuff
    bool_count = evaluation.count("or") + evaluation.count("and")
    if bool_count:
        booleans = [(i, tok) for i, tok in enumerate(evaluation) if tok == "and" or tok == "or"]
        new = ["bool("] * bool_count
        start = 0
        for n, curr in enumerate(booleans):
            i, tok = curr
            end = booleans[n + 1][0] if n + 1 < bool_count else len(evaluation)
            right_arg = evaluation[i:end] + [")"]
            if n == 0:
                left_arg = evaluation[start:i]
                temp = left_arg[:] + right_arg[:]
            else:
                temp = right_arg[:]

            new.extend(temp)
            start = i+1
        evaluation = new

    # catch ternary's
    if '?' in evaluation:
        question = evaluation.index('?')
        expr = evaluation[:question]
        colon = evaluation.index(':')
        if_true = evaluation[question + 1:colon]
        if_false = evaluation[colon+1:]
        evaluation = if_true + ["if"] + expr + ["else"] + if_false

    return evaluation


def parse_macro(tokens: List['Node']) -> int:
    scalar_tokens: List[List['Node']] = []
    for curr in tokens:
        token: List['Node'] = [curr]
        if isinstance(token[0], ast.LinesNode):
            token = cast(List['Node'], parse_lines(token[0]))
            print(token)
        while isinstance(token[0], ast.IdentifierNode):
            if token[0].children[0] in symtable.TABLE:
                token = symtable.TABLE[cast(str, token[0].children[0])].tokens
            else:
                token = [ast.PreprocessingNumberNode(["0"])]

        scalar_tokens.append(token)

    evaluation = convert_nodes_to_expr(scalar_tokens)

    final = 0
    try:
        final = eval(" ".join(evaluation))
    except SyntaxError:
        print(f"ERROR: syntax error while evaluating Macro Call")
        raise symtable.PepperSyntaxError()

    final = int(final)

    return final
