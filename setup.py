"""
A code translator using AST from Python to Ruby.
This is basically a NodeVisitor with ruby output.
See:
https://docs.python.org/3/library/ast.html
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py2rb',
    version='0.1.2',
    description='A code translator using AST from Python to Ruby',
    long_description=long_description,
    url='https://github.com/naitoh/py2rb',
    author='NAITOH Jun',
    author_email='naitoh@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='python ruby',
    packages=['py2rb'],
    package_data = {
        'py2rb': ['modules/lib.yaml',
                  'modules/numpy.yaml',
                  'modules/unittest.yaml',
                  'builtins/require.rb',
                  'builtins/module.rb', ]
    },
    install_requires=[
        'pyyaml',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'py2rb=py2rb:main'
        ]
    }
)
