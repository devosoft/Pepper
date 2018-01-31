import subprocess as sp
import shutil


SOURCE_FILE_DIRECTORY = "./tests/test_data/"
EXAMPLE_OUTPUT_DIRECTORY = "./tests/test_data/output_examples/"
CXX_FLAG = "clang"


class TestSystem:
    def test_no_preprocessing_statements(self,tmpdir):
        curr_file = "/no_preprocessing_statements.cpp"
        test_dir = tmpdir.mkdir('compiled')
        initial_file = SOURCE_FILE_DIRECTORY + curr_file

        #run Pepper output extention to (.ii)
        test_dir_path = test_dir.realpath()+(curr_file[:-3]+ 'ii' )
        process = sp.run(["Pepper", initial_file, "--output_file", test_dir_path], stdout=sp.PIPE)
        assert(process.returncode == 0)

        pepper_executable = test_dir.realpath() + "/no_preprocessing_statements.pepper"

        #run compiler using C++ 17 standard
        process = sp.run([CXX_FLAG, "-std=c++1z","-o" , pepper_executable ,test_dir_path],
                         stdout=sp.PIPE, stderr= sp.PIPE)
        assert(process.returncode == 0)

        # run executable
        pepper_process = sp.Popen([pepper_executable], stdout=sp.PIPE, stderr= sp.PIPE)
        p_out,p_err = pepper_process.communicate()



        # run normal compilation stage
        compile_executable = test_dir.realpath() + "no_preprocessing_statements." + CXX_FLAG
        process = sp.run(['g++', "-std=c++1z","-o" , compile_executable , initial_file],
                         stdout=sp.PIPE, stderr= sp.PIPE)
        assert(process.returncode == 0)

        compile_process = sp.Popen([compile_executable], stdout=sp.PIPE, stderr= sp.PIPE)
        c_out,c_err = compile_process.communicate()

        assert(p_out == c_out)
