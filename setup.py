#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'swagger_spec_validator',
    'hypothesis[datetime]',
    'furl'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='swagger_fuzzer',
    version='0.1.0',
    description="Swagger Fuzzer helps you do fuzzing testing on your Swagger APIs.",
    long_description=readme + '\n\n' + history,
    author="Boris Feld",
    author_email='lothiraldan@gmail.com',
    url='https://github.com/lothiraldan/swagger_fuzzer',
    packages=[
        'swagger_fuzzer',
    ],
    package_dir={'swagger_fuzzer':
                 'swagger_fuzzer'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='swagger_fuzzer',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts':  [
            "swagger-fuzzer = swagger_fuzzer.swagger_fuzzer:main"
        ]
    }
)
