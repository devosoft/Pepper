"""
This module contains the functions necessary to run only the preprocessor

It primarily serves as the entry point to Pepper
"""
import argparse
import pepper.parser as parser
import os
import pepper.symbol_table as symtable
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', help="the input source file")
    parser.add_argument('--output_file',
                        '-o',
                        type=argparse.FileType('w'),
                        help='the filename to write to')

    parser.add_argument('-S',
                        '--sys_include',
                        help="path to add to the system include paths",
                        action="append",
                        type=Path)

    return parser.parse_args()


def main(args=None):
    if not args:
        args = get_args()

    if args.sys_include:
        for p in args.sys_include:
            symtable.SYSTEM_INCLUDE_PATHS.append(p)

    symtable.FILE_QUEUE.append(open(args.input_file, 'r'))

    parser_input = ""

    preprocessed_lines = [""]

    while len(symtable.FILE_QUEUE):
        parser_input += symtable.FILE_QUEUE[-1].readline()

        if not len(parser_input):
            symtable.FILE_QUEUE.pop()
            if len(symtable.FILE_QUEUE):
                preprocessed_lines.append("")
        elif not parser_input.endswith(r"\\n"):
            tree = parser.parse(parser_input)
            if len(symtable.IFDEF_STACK) == 0 or symtable.IFDEF_STACK[-1][1]:
                output = tree.preprocess(preprocessed_lines)
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
