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
            self.index += 1
            return self.contents[self.index-1]

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

    if args.input_file is None:
        fake_input_file = None

        with open(SOURCE_FILE_DIRECTORY + source, 'r') as sourcefile:
            fake_input_file = FakeFile(f"{SOURCE_FILE_DIRECTORY}{source}", sourcefile.readlines())

        args.input_file = fake_input_file

    fake_output_file = FakeFile(f"{source}.fake_output")
    args.output_file = fake_output_file

    preprocessor.main(args)

    if isinstance(reference, FakeFile):
        assert(args.output_file.contents == reference.contents)
    else:
        with open(EXAMPLE_OUTPUT_DIRECTORY + reference) as reference_file:
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
    with open(f'{EXAMPLE_OUTPUT_DIRECTORY}{reference}', 'r') as expected_file:
        with open(f"{test_dir.realpath()}/{source}.preprocessed.cc") as outfile:
            assert(outfile.read() == expected_file.read())


class TestUnit:
    def setup_method(self, method):
        reset_state()

    def test_comments(self, tmpdir):
        preprocess_and_compare_functionally('comments.cpp', 'comments.cpp.preprocessed.cc')

    def test_nested_macro_expansion(self, tmpdir):
        preprocess_and_compare_functionally('multiple_macros.cpp',
                                            'multiple_macros.cpp.preprocessed.cc')

    def test_function_and_macro_calls(self, tmpdir):
        preprocess_and_compare_functionally('function_and_macro_calls.cpp',
                                            'function_and_macro_calls.cpp.preprocessed.cc')

    def test_function_and_macro_calls_2(self, tmpdir):
        preprocess_and_compare_functionally('function_like_macro_2.cpp',
                                            'function_like_macro_2.cpp.preprocessed.cc')

    def test_basic_function_with_defaults_refactored(self, tmpdir):
        preprocess_and_compare("file_include.cpp",
                               "preprocessed_file_include.cpp",
                               tmpdir,
                               ['SomeFile.h', 'SomeOtherFile.h'])

    def test_ifdef_handling(self, tmpdir):
        preprocess_and_compare_functionally('ifdef.cpp', 'ifdef.cpp.preprocessed.cc')

    def test_for_loop_not_breaking_macros(self, tmpdir):
        preprocess_and_compare_functionally("for_loop.cpp", "for_loop.cpp.preprocessed.cc")

    def test_variadic_macro_expansion(self, tmpdir):
        ifile_contents = [
            "#define somemacro(a, b, moar...) a + b + mult(moar)\n",
            "int main {\n",
            "   cout << somemacro(1, 2, 3, 4, 5, 6) << endl;\n",
            "}",
        ]
        expected_out = [
            "// Macro somemacro with args ['a', 'b', 'moar...'] expanding to 'a + b + mult(moar)'", # NOQA
            "int main {",
            "   cout << 1 + 2 + mult(3, 4, 5, 6) << endl;",
            "}",
            "",
        ]

        args = FakeArgs()
        args.input_file = FakeFile('variadic_expand.cc', ifile_contents)
        expected_out_file = FakeFile('whatever', expected_out)

        preprocess_and_compare_functionally(None, expected_out_file, args)

    def test_system_file_include(self, tmpdir):
        system_dir = tmpdir.mkdir('system_include_path')

        args = FakeArgs()
        args.sys_include = [system_dir.realpath()]
        # copy some files to the tmpdir, then run search for them

        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeFile.h', f"{system_dir.realpath()}/SomeFile.h")
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeOtherFile.h',
                    f"{system_dir.realpath()}/SomeOtherFile.h")

        preprocess_and_compare_functionally('systemish_include.cpp',
                                            'systemish_include.cpp.preprocessed.cc',
                                            args)

    def test_include_path_search(self, tmpdir):
        # copy some files to the tmpdir, then run search for them
        test_dir = tmpdir.mkdir('include_path')
        shutil.copy(SOURCE_FILE_DIRECTORY + 'SomeFile.h', test_dir.realpath())
        symtable.SYSTEM_INCLUDE_PATHS.append(str(test_dir.realpath()))

        found = ast.PreprocessorIncludeNode.search_system_includes('SomeFile.h')
        expected = Path(f"{test_dir.realpath()}/{'SomeFile.h'}")

        assert(found and (found == expected))

        try:
            found = ast.PreprocessorIncludeNode.search_system_includes('FileThatDoesNotExist.h')
            assert(False and "There should have been an OSError!")
        except OSError as err:
            assert("Could not find file FileThatDoesNotExist.h in defined system include paths:" in str(err)) # NOQA

    def test_error_raised_for_bad_syntax(self, tmpdir):
        test_dir = tmpdir.mkdir('preprocessor')
        # copy the test file to the test directory
        shutil.copy(SOURCE_FILE_DIRECTORY + "error.cpp", test_dir.realpath())

        exception_raised = False
        try:
            # doesn't actually matter what the reference is
            preprocess_and_compare_functionally('error.cpp', 'preprocessed_file_include.cpp')
            assert(False and "Should have had an exception thrown!")
        except symtable.PepperSyntaxError as err:
            exception_raised = True

        assert(exception_raised)

    def test_internal_error_handling(self, tmpdir):
        args = FakeArgs()
        args.trigger_internal_error = True

        exception_raised = False
        try:
            preprocess_and_compare_functionally('function_like_macro_2.cpp',
                                                'function_like_macro_2.cpp.preprocessed.cc',
                                                args)
            assert(False and "Should have had an exception thrown!")
        except symtable.PepperInternalError as err:
            exception_raised = True

        assert(exception_raised)

    def test_if_basic_expressions(self, tmpdir):
        preprocess_and_compare_functionally('if_expressions.cpp',
                                            'if_expressions.cpp.preprocessed.cc')

    def test_if_macro_calls(self, tmpdir):
        preprocess_and_compare_functionally('if_macro_expressions.cpp',
                                            'if_macro_expressions.cpp.preprocessed.cc')

    def test_if_with_file_includes(self, tmpdir):
        preprocess_and_compare("file_include_if.cpp", "file_include_if.preprocessed.cc",
                               tmpdir,
                               ['SomeFile.h', 'SomeOtherFile.h'])

    def test_error_raised_if_token_syntax(self, tmpdir):
        in_contents = [
            "#define M1(a,b) a + b\n",
            "#if M1(12.2, 12.1 *0.23)\n",
            "#endif"
        ]

        expected = [""]

        args = FakeArgs()
        args.input_file = FakeFile("type_error.cc", in_contents)
        expected_file = FakeFile("whatever", expected)

        exception_raised = False
        try:
            # doesn't actually matter what the reference is
            preprocess_and_compare_functionally(None, expected_file, args)
            assert(False and "Should have had an exception thrown!")
        except symtable.PepperSyntaxError as err:
            exception_raised = True

        assert(exception_raised)

    def test_error_raised_macro_eval_syntax(self, tmpdir):
        in_contents = [
            "#define M1(a,b) a and or and b\n",
            "#if M1(1, 2)\n",
            "#endif"
        ]

        expected = [""]

        args = FakeArgs()
        args.input_file = FakeFile("macro_error.cc", in_contents)
        expected_file = FakeFile("whatever", expected)

        exception_raised = False
        try:
            # doesn't actually matter what the reference is
            preprocess_and_compare_functionally(None, expected_file, args)
            assert(False and "Should have had an exception thrown!")
        except symtable.PepperSyntaxError as err:
            exception_raised = True

        assert(exception_raised)



class TestSystem:
    def test_basic_function(self, tmpdir):
        preprocess_and_compare("file_include.cpp",
                               "preprocessed_file_include.cpp",
                               tmpdir,
                               ['SomeFile.h', 'SomeOtherFile.h'])
