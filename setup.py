#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests'
]

setup(
    name='simple_zpl2',
    version='0.3.0',
    description="For building ZPL2 strings for printing barcodes with Zebra or compatible label printers.",
    long_description=readme + '\n\n' + history,
    author="Joe Sacher",
    author_email='sacherjj@gmail.com',
    url='https://github.com/sacherjj/simple_zpl2',
    packages=[
        'simple_zpl2',
    ],
    package_dir={'simple_zpl2':
                 'simple_zpl2'},
    entry_points={
        'console_scripts': [
            'simple_zpl2=simple_zpl2.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='simple_zpl2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
