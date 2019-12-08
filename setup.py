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
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License',
    ],
    keywords=['env-alias', 'shell', 'env', 'alias', 'bash'],

    author='Nicholas de Jong',
    author_email='contact@nicholasdejong.com',
    url='https://github.com/ndejong/env-alias',
    license='BSD 2-Clause',

    packages=find_packages(),
    zip_safe=False,
    scripts=['bin/env-alias', 'bin/env-alias-generator'],

    install_requires=['pyyaml'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],

)
