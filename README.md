# Pepper
[![TravisCI Status](https://api.travis-ci.org/devosoft/Pepper.svg?branch=master)](https://github.com/devosoft/Pepper/)
[![ReadTheDocs Status](https://readthedocs.org/projects/pepper/badge/?version=latest)](https://github.com/devosoft/Pepper/)

Pepper is the brainchild of Dr. Charles Ofria.

The Pepper documentation is available at [ReadTheDocs](http://pepper.readthedocs.io/en/latest/) and the developer blog is available on the [Github Pages site](https://devosoft.github.io/Pepper/).

The end goal is to have a piece of c++ code that looks like:

```
#define SHARED_NAMESPACE;

#py if(pepper.SHARED_NAMESPACE):
#py     pepper.GREETING = "Hello from Pepper, world!"

#include <iostream>

void main() {
    std::cout << GREETING << std::endl;
}
```

The current general plan is that python blocks will be executed as the program is processed and
any output from them will be inserted into the processed file.

Python code will not be callable once compiled, but any output emitted by the python program will be concatenated into the c++ code.

The preprocessor symbol table will be shared between c-style macros and Pepper calls.

## Dependencies

Dependencies are auto-installed with pip-based installation, i.e. `pip install .`

System-level prerequisites are Python 3.6 and pip.

## Invoking Pepper

Once installed (`pip install .`) the command `Pepper` will be available. This invokes the preprocessor:

```
$ Pepper
usage: Pepper [-h] [--output_file OUTPUT_FILE] [-S SYS_INCLUDE] input_file
Pepper: error: the following arguments are required: input_file
```

Pepper's argument parser will dump help output if it is invoked incorrectly. Pepper takes the following arguments:

```
usage: Pepper [-h] [--output_file OUTPUT_FILE] [-S SYS_INCLUDE] input_file

positional arguments:
  input_file            the input source file

optional arguments:
  -h, --help            show this help message and exit
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        the filename to write to
  -S SYS_INCLUDE, --sys_include SYS_INCLUDE
                        path to add to the system include paths

```

## To test

`make test` or

 ```
 PYTHONPATH=`pwd` pytest
 ```

 ## To metric test coverage

 ```
 py.test --cov-report=html --cov=pepper
 ```