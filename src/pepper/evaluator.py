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


def validate(exp, line_no):
    literal = None
    if isinstance(exp, ast.PreprocessingNumberNode):
        literal = exp.children[0]
    elif isinstance(exp, ast.StringLiteralNode):
        literal = str(ord(exp.children[0][1]))
    elif isinstance(exp, ast.ASCIILiteralNode):
        literal = exp.children[0]
    elif isinstance(exp, ast.OperatorNode):
        child = exp.children[0]
        if child == '&&':
            literal = 'and'
        elif child == '||':
            literal = 'or'
        else:
            literal = child
    elif isinstance(exp, int) or isinstance(exp, bool):
        literal = str(exp)

    return literal


def parse_line(t):
    if isinstance(t[0], ast.LinesNode):
        return parse_lines(t[0])
    # while isinstance(t[0], ast.IdentifierNode):
    #    if t[0].children[0] in symtable.TABLE:
    #        t = symtable.TABLE[t[0].children[0]].tokens
    #    else:
    #        t = [0]

    return t


def parse_lines(token):
    return [parse_line([t]) for t in token.children]


def unravel_list(exp):
    parsing = []
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


def parse_macro(tokens, line_no=0):
    scalar_tokens = []
    for token in tokens:
        token = [token]
        if isinstance(token[0], ast.LinesNode):
            token = parse_lines(token[0])
        while isinstance(token[0], ast.IdentifierNode):
            if token[0].children[0] in symtable.TABLE:
                token = symtable.TABLE[token[0].children[0]].tokens
            else:
                token = [0]

        scalar_tokens.append(token)

    evaluation = []

    # no defined macros will accepted if not an integer type
    for expr in scalar_tokens:
        for exp in expr:
            if isinstance(exp, list):
                exp = unravel_list(exp)
                exp = [validate(tok, line_no) for tok in exp
                       if not isinstance(tok, ast.WhiteSpaceNode)]
                evaluation.extend(exp)
            elif exp == "(" or exp == ")":
                evaluation.append(exp)
            elif not isinstance(exp, ast.WhiteSpaceNode):
                exp = validate(exp, line_no)
                evaluation.append(exp)

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

    # catch AND  && OR stuff
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

    try:
        final = eval(" ".join(evaluation))
    except SyntaxError:
        print(f"ERROR: syntax error while evaluating Macro Call")
        raise symtable.PepperSyntaxError()

    if isinstance(final, float):
        final = int(final)

    return final
