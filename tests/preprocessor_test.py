# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

import subprocess
import shutil
import sys
from pathlib import Path

import pepper.symbol_table as symtable
import pepper.abstract_symbol_tree as ast
import pepper.preprocessor as preprocessor

SOURCE_FILE_DIRECTORY = "./tests/test_data/"
EXAMPLE_OUTPUT_DIRECTORY = "./tests/test_data/output_examples/"


class FakeFile():
    def __init__(self, name, contents=None):
        self.name = name
        self.contents = contents if contents else []
        self.index = 0

    def readline(self):
        if self.index >= len(self.contents):
            return ""
        else:
            annoying_temp_var = self.contents[self.index]
            self.index += 1
            return annoying_temp_var

    def close(self):
        pass

    def write(self, lines):
        self.contents.extend(lines.split("\n"))

    def get_contents(self):
        return "\n".join(self.contents)

    def name(self):
        return self.name


class FakeArgs():
    def __init__(self):
        self.input_file = None
        self.output_file = None
        self.trigger_internal_error = False
        self.sys_include = False
        self.debug = True


def preprocess_and_compare_functionally(source, reference, prebuilt_args_object=None):
    args = None
    if prebuilt_args_object:
        args = prebuilt_args_object
    else:
        args = FakeArgs()
        fake_input_file = None

        with open(SOURCE_FILE_DIRECTORY + source, 'r') as sourcefile:
            fake_input_file = FakeFile(f"{SOURCE_FILE_DIRECTORY}{source}", sourcefile.readlines())

        args.input_file = fake_input_file

        fake_output_file = FakeFile(f"{source}.fake_output")
        args.output_file = fake_output_file

    preprocessor.main(args)

    with open(EXAMPLE_OUTPUT_DIRECTORY + reference) as reference_file:
        # import pdb; pdb.set_trace();
        assert(args.output_file.get_contents() == reference_file.read())


def reset_state():
    symtable.TABLE = dict()
    symtable.FILE_STACK = []
    symtable.IFDEF_STACK = []
    symtable.SYSTEM_INCLUDE_PATHS = []
    symtable.EXPANDED_MACRO = False
    symtable.TRIGGER_INTERNAL_ERROR = False


def preprocess_and_compare(source, reference, tmpdir, supportfiles=[], optional_args=[]):
    test_dir = tmpdir.mkdir('preprocessor')
    # copy the test file to the test directory
    shutil.copy(SOURCE_FILE_DIRECTORY + source, test_dir.realpath())

    for entry in supportfiles:
        shutil.copy(SOURCE_FILE_DIRECTORY + entry, test_dir.realpath())

    call = ["Pepper"] + optional_args + [f"{test_dir.realpath()}/{source}"]

    process = subprocess.run(call, timeout=2, stdout=sys.stdout, stderr=sys.stderr)
    # out, err = process.communicate()
    assert(process.returncode == 0)
    with open(f'{EXAMPLE_OUTPUT_DIRECTORY}{reference}', 'r') as expected_file: # NOQA
        with open(f"{test_dir.realpath()}/{source}.preprocessed.cc") as outfile:
            assert(outfile.read() == expected_file.read())


class TestUnit:
    def setup_method(self, method):
        reset_state()

    def test_comments(self, tmpdir):
        preprocess_and_compare_functionally('comments.cpp', 'comments.cpp.preprocessed.cc')

    def test_nested_macro_expansion(self, tmpdir):
        preprocess_and_compare_functionally('multiple_macros.cpp', 'multiple_macros.cpp.preprocessed.cc')

    def test_function_and_macro_calls(self, tmpdir):
        preprocess_and_compare_functionally('function_and_macro_calls.cpp', 'function_and_macro_calls.cpp.preprocessed.cc')  # NOQA

    def test_function_and_macro_calls_2(self, tmpdir):
        preprocess_and_compare_functionally('function_like_macro_2.cpp', 'function_like_macro_2.cpp.preprocessed.cc')  # NOQA

    def test_basic_function_with_defaults_refactored(self, tmpdir):
        preprocess_and_compare_functionally('file_include.cpp', 'preprocessed_file_include.cpp')

    def test_ifdef_handling(self, tmpdir):
        preprocess_and_compare_functionally('ifdef.cpp', 'ifdef.cpp.preprocessed.cc')

    def test_for_loop_not_breaking_macros(self, tmpdir):
        preprocess_and_compare_functionally("for_loop.cpp", "for_loop.cpp.preprocessed.cc")

    def test_include_path_search(self, tmpdir):
        # copy some files to the tmpdir, then run search for them
        test_dir = tmpdir.mkdir('include_path')
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeFile.h', test_dir.realpath())
        symtable.SYSTEM_INCLUDE_PATHS.append(str(test_dir.realpath()))

        found = ast.PreprocessorIncludeNode.search_system_includes('SomeFile.h')
        expected = Path(f"{test_dir.realpath()}/{'SomeFile.h'}")

        assert(found is not False)
        assert(found == expected)

        try:
            found = ast.PreprocessorIncludeNode.search_system_includes('FileThatDoesNotExist.h')
            assert(False and "There should have been an OSError!")
        except OSError as err:
            assert("Could not find file FileThatDoesNotExist.h in defined system include paths:" in str(err)) # NOQA


class TestSystem:
    def test_basic_function(self, tmpdir):
        outfile = tmpdir.mkdir('preprocessor').join("file_include.cpp.preprocessed.cpp")
        process = subprocess.run(["Pepper", "./tests/test_data/file_include.cpp", "--output_file",
                                 str(outfile.realpath())], timeout=2, stdout=subprocess.PIPE)
        # out, err = process.communicate()
        assert(process.returncode == 0)
        with open('tests/test_data/output_examples/preprocessed_file_include.cpp', 'r') as expected_file: # NOQA
            assert(outfile.read() == expected_file.read())

    def test_system_file_include(self, tmpdir):
        # copy some files to the tmpdir, then run search for them
        system_dir = tmpdir.mkdir('system_include_path')
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeFile.h', f"{system_dir.realpath()}/SomeFile.h")
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeOtherFile.h',
                    f"{system_dir.realpath()}/SomeOtherFile.h")

        preprocess_and_compare('systemish_include.cpp', 'systemish_include.cpp.preprocessed.cc',
                               tmpdir, optional_args=['-S', str(system_dir.realpath())])

    def test_error_raised_for_bad_syntax(self, tmpdir):
        test_dir = tmpdir.mkdir('preprocessor')
        # copy the test file to the test directory
        shutil.copy(SOURCE_FILE_DIRECTORY + "error.cpp", test_dir.realpath())

        call = ["Pepper"] + [f"{test_dir.realpath()}/error.cpp"]

        process = subprocess.run(call, timeout=2, stdout=subprocess.PIPE)
        # out, err = process.communicate()
        assert(process.returncode == 1)
        exception_clippings = [
            "A syntax error was encountered while parsing a line from",
            "error.cpp",
            "#define thisisamacro(wait noO IT'S A SYNTAX ERROR"
        ]
        data = process.stdout.decode('utf-8')
        for clip in exception_clippings:
            assert(clip in data)

    def test_internal_error_handling(self, tmpdir):
        test_dir = tmpdir.mkdir('preprocessor')
        # copy the test file to the test directory
        shutil.copy(SOURCE_FILE_DIRECTORY + "function_like_macro_2.cpp", test_dir.realpath())

        call = ["Pepper"] + ["--trigger_internal_error"]
        call += [f"{test_dir.realpath()}/function_like_macro_2.cpp"]

        process = subprocess.run(call, timeout=2, stdout=subprocess.PIPE)
        # out, err = process.communicate()
        assert(process.returncode == 2)
        exception_clippings = [
            "An internal error occured while processing a line:",
            "Please report this error: https://github.com/devosoft/Pepper/issues",
        ]
        data = process.stdout.decode('utf-8')
        for clip in exception_clippings:
            assert(clip in data)

