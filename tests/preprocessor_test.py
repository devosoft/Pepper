# This file is a part of the Pepper project, https://github.com/devosoft/Pepper
# (C) Michigan State University, under the MIT License
# See LICENSE.txt for more information

import subprocess
import shutil
import sys
from pathlib import Path

import pepper.symbol_table as symtable
import pepper.abstract_symbol_tree as ast

SOURCE_FILE_DIRECTORY = "./tests/test_data/"
EXAMPLE_OUTPUT_DIRECTORY = "./tests/test_data/output_examples/"


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


# bad test now, good test later...?
class TestSystem:
    def test_basic_function(self, tmpdir):
        outfile = tmpdir.mkdir('preprocessor').join("file_include.cpp.preprocessed.cpp")
        process = subprocess.run(["Pepper", "./tests/test_data/file_include.cpp", "--output_file",
                                 str(outfile.realpath())], timeout=2, stdout=subprocess.PIPE)
        # out, err = process.communicate()
        assert(process.returncode == 0)
        with open('tests/test_data/output_examples/preprocessed_file_include.cpp', 'r') as expected_file: # NOQA
            assert(outfile.read() == expected_file.read())

    def test_basic_function_with_defaults_refactored(self, tmpdir):
        preprocess_and_compare('file_include.cpp', 'preprocessed_file_include.cpp',
                               tmpdir, ['SomeFile.h', 'SomeOtherFile.h'])

    def test_ifdef_handling(self, tmpdir):
        preprocess_and_compare('ifdef.cpp', 'ifdef.cpp.preprocessed.cc', tmpdir)

    def test_system_file_include(self, tmpdir):
        # copy some files to the tmpdir, then run search for them
        system_dir = tmpdir.mkdir('system_include_path')
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeFile.h', f"{system_dir.realpath()}/SomeFile.h")
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeOtherFile.h',
                    f"{system_dir.realpath()}/SomeOtherFile.h")

        preprocess_and_compare('systemish_include.cpp', 'systemish_include.cpp.preprocessed.cc',
                               tmpdir, optional_args=['-S', system_dir.realpath()])

    def test_comments(self, tmpdir):
        preprocess_and_compare('comments.cpp', 'comments.cpp.preprocessed.cc', tmpdir)

    def test_nested_macro_expansion(self, tmpdir):
        preprocess_and_compare('multiple_macros.cpp', 'multiple_macros.cpp.preprocessed.cc', tmpdir)

    def test_function_and_macro_calls(self, tmpdir):
        preprocess_and_compare('function_and_macro_calls.cpp', 'function_and_macro_calls.cpp.preprocessed.cc', tmpdir)  # NOQA

    def test_function_and_macro_calls_2(self, tmpdir):
        preprocess_and_compare('function_like_macro_2.cpp', 'function_like_macro_2.cpp.preprocessed.cc', tmpdir)  # NOQA

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

    # def test_internal_error_caught_and_reported(self, tmpdir):
    #     # if we don't pass args, it'll just blow up
    #     err_raised = False
    #     try:
    #         preprocessor.main()
    #         assert(False and "There should have been an error raised!")
    #     except symtable.PepperInternalError as err:
    #         err_raised = True
    #     except:  # NOQA
    #         assert(False and "Wrong type of exception raised!")
    #     assert(err_raised)

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

    def test_for_loop_not_breaking_macros(self, tmpdir):
        preprocess_and_compare("for_loop.cpp", "for_loop.cpp.preprocessed.cc", tmpdir)
