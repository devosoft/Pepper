# import pepper.preprocessor as preproc
import subprocess
import shutil

SOURCE_FILE_DIRECTORY = "./tests/test_data/"
EXAMPLE_OUTPUT_DIRECTORY = "./tests/test_data/output_examples/"


def preprocess_and_compare(source, reference, tmpdir, supportfiles=[]):
    test_dir = tmpdir.mkdir('preprocessor')
    # copy the test file to the test directory
    shutil.copy(SOURCE_FILE_DIRECTORY + source, test_dir.realpath())

    for entry in supportfiles:
        shutil.copy(SOURCE_FILE_DIRECTORY + entry, test_dir.realpath())

    process = subprocess.run(["Pepper", f"{test_dir.realpath()}/{source}"], timeout=2,
                             stdout=subprocess.PIPE)
    # out, err = process.communicate()
    assert(process.returncode == 0)
    with open(f'{EXAMPLE_OUTPUT_DIRECTORY}preprocessed_file_include.cpp', 'r') as expected_file: # NOQA
        with open(f"{test_dir.realpath()}/{source}.preprocessed.cc") as outfile:
            assert(outfile.read() == expected_file.read())


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
        preprocess_and_compare('file_include.cpp', 'preprocessed_file_include.cpp', tmpdir, ['SomeFile.h', 'SomeOtherFile.h'])
