# Pepper
[![TravisCI Status](https://api.travis-ci.org/devosoft/Pepper.svg?branch=master)](https://github.com/devosoft/Pepper/https://travis-ci.org/devosoft/Pepper/branches)
[![ReadTheDocs Status](https://readthedocs.org/projects/pepper/badge/?version=latest)](http://pepper.readthedocs.io/en/latest/)
[![PyPI version](https://badge.fury.io/py/Pepper.svg)](https://badge.fury.io/py/Pepper)

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

The preprocessor will also implement all existing functionality within the C Preprocessor so that it can be used as a replacement.

## Dependencies

To install dev dependencies in an editable pip install, use the command:

```
$ pip install -e . .[develop]
```

System-level prerequisites are Python 3.6 and pip.

## Invoking Pepper

Pepper can be installed via pip:

```
$ pip install pepper
```

Once installed the command `Pepper` will be available. This invokes the preprocessor:

```
$ Pepper
usage: Pepper [-h] [--output_file OUTPUT_FILE] [-S SYS_INCLUDE] input_file
Pepper: error: the following arguments are required: input_file
```

## To test

`make test` or `pytest`
