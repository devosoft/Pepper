
# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

"""
This module contains the functions necessary to run only the preprocessor

It primarily serves as the entry point to Pepper
"""

import argparse
import pepper.parser as parser
from pepper import __version__
import os
import pepper.symbol_table as symtable
from pathlib import Path
import sys


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', help="the input source file")
    parser.add_argument('--output_file',
                        '-o',
                        type=argparse.FileType('w'),
                        help='the filename to write to')

    parser.add_argument('--version', help="output Pepper's version and halt.",
                        action='version',
                        version=f"Pepper {__version__}")

    parser.add_argument('-S',
                        '--sys_include',
                        help="path to add to the system include paths",
                        action="append",
                        type=Path)

    parser.add_argument('--trigger_internal_error',
                        help="testing switch to cause an internal error",
                        action="store_true")

    parser.add_argument('--debug', help="enable debugging output", action="store_true")

    return parser.parse_args()


def main(args=None):
    if not args:
        args = get_args()

    if args.sys_include:
        for p in args.sys_include:
            symtable.SYSTEM_INCLUDE_PATHS.append(p)

    if args.trigger_internal_error:
        symtable.TRIGGER_INTERNAL_ERROR = True

    symtable.FILE_STACK.append(open(args.input_file, 'r'))

    parser_input = ""

    preprocessed_lines = [""]
    tree = None

    while len(symtable.FILE_STACK):
        if symtable.EXPANDED_MACRO:
            symtable.EXPANDED_MACRO = False
            # lexer eats the newlines, have to re-add them
            parser_input = "\n" + preprocessed_lines[-2] + "\n"
            preprocessed_lines = preprocessed_lines[:-2]
        else:
            parser_input += symtable.FILE_STACK[-1].readline()

        if not len(parser_input):
            symtable.FILE_STACK.pop()
            if len(symtable.FILE_STACK):
                preprocessed_lines.append("")
        elif not parser_input.endswith(r"\\n"):
            try:
                tree = parser.parse(parser_input, args.debug if args.debug else None)
            except symtable.PepperSyntaxError:
                print(f"A syntax error was encountered while parsing a line from {symtable.FILE_STACK[-1].name}:")  # NOQA
                print(f"{parser_input}")
                sys.exit(1)
            if len(symtable.IFDEF_STACK) == 0 or symtable.IFDEF_STACK[-1][1]:
                try:
                    output = tree.preprocess(preprocessed_lines)
                except Exception as err:
                    print("An internal error occured while processing a line:")
                    print(f"{parser_input}")
                    print("Please report this error: https://github.com/devosoft/Pepper/issues")
                    print(f"{err}")
                    sys.exit(2)
            else:
                pass  # toss the line, we're in a 'deny' ifdef
            parser_input = ""

    # source = args.input_file.read()

    # parser.parse(source).preprocess(preprocessed_lines)
    output = "\n".join(preprocessed_lines) + "\n"

    if args.output_file:
        args.output_file.write(output)
        args.output_file.close()
    else:
        basepath = os.path.split(args.input_file)[0]
        with open(basepath + '/' + os.path.split(args.input_file)[1] + ".preprocessed.cc", 'w') as output_file: # NOQA
            output_file.write(output)


if __name__ == "__main__":
    main()
