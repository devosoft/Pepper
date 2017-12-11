"""
This module contains the functions necessary to run only the preprocessor

It primarily serves as the entry point to Pepper
"""
import argparse
import pepper.parser as parser


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_file', type=argparse.FileType('r'), help="the input source file")
    parser.add_argument('--output_file',
                        '-o',
                        type=argparse.FileType('w'),
                        help='the filename to write to')

    return parser.parse_args()


def main(args=None):
    if not args:
        args = get_args()

    source = "\n".join(args.input_file.readlines())

    preprocessed_lines = []
    parser.parse(source).preprocess(preprocessed_lines)
    output = "\n".join(preprocessed_lines)

    if args.output_file:
        args.output_file.write(output)
        args.output_file.close()
    else:
        with open(args.input_file.name + ".preprocessed.cc", 'w') as output_file:
            output_file.write("\n".join(output))


if __name__ == "__main__":
    main()
