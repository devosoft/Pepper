# import pepper.preprocessor as preproc
import subprocess


# bad test now, good test later...?
class TestSystem:
    def test_basic_function(self, tmpdir):
        outfile = tmpdir.mkdir('preprocessor').join("file_include.cpp.preprocessed.cpp")
        process = subprocess.run(["Pepper", "./tests/test_data/file_include.cpp", "--output_file", str(outfile.realpath())], timeout=2,
                                  stdout=subprocess.PIPE)
        # out, err = process.communicate()
        assert(process.returncode == 0)
        with open('tests/test_data/output_examples/preprocessed_file_include.cpp', 'r') as expected_file:
            assert(outfile.read() == expected_file.read())