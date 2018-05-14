#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# thanks to https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure for this template
from __future__ import absolute_import
from __future__ import print_function

import io
import versioneer

from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='Pepper',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license='MIT License',
    description='Python-Enhanced PrePreocessor',
    author='Jake Fenton',
    author_email='jake@fenton.io',
    url='https://github.com/Devosoft/Pepper',
    download_url=f'https://github.com/devosoft/Pepper/archive/{versioneer.get_version()}.tar.gz',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    keywords=[
        'preprocessor', 'C', 'C++', 'ply', 'compiler',
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'versioneer',
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
    ],
    extras_require={
        'develop': [
            'diff_cover',
            'flake8',
            'ply>=3.10',
            'pytest-cov',
            'pytest',
            'sphinx>=1.6.3',
            'tox',
            'wheel',
             ]
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    entry_points={
        'console_scripts': [
            'PepperParse = pepper.parser:main',
            'PepperLex = pepper.lexer:main',
            'Pepper = pepper.preprocessor:main',
        ]
    },
)
