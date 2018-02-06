import subprocess as sp
import shutil


SOURCE_FILE_DIRECTORY = "./tests/test_data/"
EXAMPLE_OUTPUT_DIRECTORY = "./tests/test_data/output_examples/"
CXX_FLAG = "g++"




class TestSystem:
    def test_no_preprocessing_statements(self,tmpdir):
        curr_file = "/no_preprocessing_statements."
        test_dir = tmpdir.mkdir('compiled')
        initial_file = SOURCE_FILE_DIRECTORY + curr_file + "cpp"

        #run Pepper output extention to (.ii)
        test_file_path = test_dir.realpath()+ curr_file + 'ii'
        process = sp.run(["Pepper", initial_file, "--output_file", test_file_path], stdout=sp.PIPE)
        assert(process.returncode == 0)

        pepper_executable = test_dir.realpath() + curr_file + "pepper"

        #run compiler using C++ 11 standard
        process = sp.run([CXX_FLAG, "-std=c++11","-Wall","-o" , pepper_executable ,test_file_path],
                         stdout=sp.PIPE, stderr= sp.PIPE)
        assert(process.returncode == 0)

        # run executable
        pepper_process = sp.Popen([pepper_executable], stdout=sp.PIPE, stderr= sp.PIPE)
        p_out,p_err = pepper_process.communicate()



        # run normal compilation stage
        compile_executable = test_dir.realpath() + curr_file  + CXX_FLAG
        process = sp.run([CXX_FLAG, "-std=c++11","-Wall" ,"-o" , compile_executable , initial_file],
                         stdout=sp.PIPE, stderr= sp.PIPE)
        assert(process.returncode == 0)

        compile_process = sp.Popen([compile_executable], stdout=sp.PIPE, stderr= sp.PIPE)
        c_out,c_err = compile_process.communicate()

        assert(p_out == c_out)
