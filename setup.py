#!/usr/bin/env python3

from setuptools import setup, find_packages
from EnvAlias import NAME
from EnvAlias import VERSION

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    description='Shell alias environment variable helper tool to load secret values and others.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    classifiers=[
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='env-alias shell env alias bash',

    author='Nicholas de Jong',
    author_email='contact@nicholasdejong.com',
    url='https://github.com/ndejong/env-alias',
    license='BSD 2-Clause',

    packages=find_packages(),
    scripts=['bin/env-alias'],

    install_requires=['pyyaml'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

)
