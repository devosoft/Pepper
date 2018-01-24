# import pepper.preprocessor as preproc
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
