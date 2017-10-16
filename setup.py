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

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='py2rb',
    version='1.0.0',
    description='A code translator using AST from Python to Ruby',
    long_description=long_description,
    url='https://github.com/naitoh/py2rb',
    author='Naitoh Jun',
    author_email='naitoh@github.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='python ruby',
    packages=find_packages(exclude=['tests']),
    install_requires=['pyyaml'],
    entry_points={
        'console_scripts': [
            'py2rb=py2rb:main'
        ]
    }
)
