# Pepper
[![TravisCI Status](https://api.travis-ci.org/devosoft/Pepper.svg?branch=master)](https://github.com/devosoft/Pepper/)
[![ReadTheDocs Status](https://readthedocs.org/projects/pepper/badge/?version=latest)](https://github.com/devosoft/Pepper/)

Pepper is the brainchild of Dr. Charles Ofria.

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

Python code will not be callable once compiled.

The preprocessor symbol table will be shared between c-style macros and Pepper calls.

## Dependencies

ply, pytest

## To test

`make test` or

 ```
 PYTHONPATH=`pwd` pytest
 ```

 ## To metric test coverage

 ```
 py.test --cov-report=html --cov=pepper
 ```