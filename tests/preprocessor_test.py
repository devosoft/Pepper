# import pepper.preprocessor as preproc
import subprocess

# bad test now, good test later...?
class TestSystem:
    def test_basic_function(self):
        process = subprocess.run(["Pepper", "./tests/test_data/file_include.cpp"], timeout=2,
                                  stdout=subprocess.PIPE)
        # out, err = process.communicate()
        assert(process.returncode == 0)
