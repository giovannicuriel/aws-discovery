# -*- coding: utf-8 -*-
"""
setup.py script
"""

import io
from collections import OrderedDict
from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding='utf8') as f:
    README = f.read()

setup(
    name='aws-discovery',
    version='1.0.0',
    url='http://github.com/giovannicuriel/aws-discovery',
    project_urls=OrderedDict((
        ('Code', 'https://github.com/giovannicuriel/aws-discovery.git'),
        ('Issue tracker', 'https://github.com/giovannicuriel/aws-discovery/issues'),
    )),
    license='BSD-3-Clause',
    author='Giovanni Curiel dos Santos',
    author_email='giovannicuriel@gmail.com',
    description='Tool to gather all configured AWS resources',
    long_description=README,
    packages=["awsdiscovery"],
    include_package_data=True,
    zip_safe=False,
    platforms=[any],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'boto3==1.9.218'
    ],
    extras_require={
        "dev": [
            "Sphinx==2.2.0",
            "pylint==2.3.1"
        ]
    }
)
