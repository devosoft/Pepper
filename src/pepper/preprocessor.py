"""
This module contains the functions necessary to run only the preprocessor

It primarily serves as the entry point to Pepper
"""
import argparse
import pepper.parser as parser
import os
import pepper.symbol_table as symtable


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', help="the input source file")
    parser.add_argument('--output_file',
                        '-o',
                        type=argparse.FileType('w'),
                        help='the filename to write to')

    return parser.parse_args()


def main(args=None):
    if not args:
        args = get_args()

    symtable.FILE_QUEUE.append(open(args.input_file, 'r'))

    parser_input = ""

    preprocessed_lines = [""]

    while len(symtable.FILE_QUEUE):
        if len(symtable.IFDEF_STACK) == 0:
            parser_input += symtable.FILE_QUEUE[-1].readline()
        elif symtable.IFDEF_STACK[-1][1]:
            parser_input += symtable.FILE_QUEUE[-1].readline()
        else:
            symtable.FILE_QUEUE[-1].readline() # toss the line, we're in a 'deny' ifdef
        if not len(parser_input):
            symtable.FILE_QUEUE.pop()
            if len(symtable.FILE_QUEUE):
                preprocessed_lines.append("")
        elif not parser_input.endswith(r"\\n"):
            output = parser.parse(parser_input).preprocess(preprocessed_lines)
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
