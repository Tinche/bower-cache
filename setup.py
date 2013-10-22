# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

import registry

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = registry.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print(" git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    print(" git push --tags")
    sys.exit()

readme = open('README.md').read()

setup(
    name='bower-cache',
    version=VERSION,
    description='A local caching proxy for Bower packages.',
    long_description=readme + '\n\n',
    author='Tin Tvrtkovic',
    author_email='tinchester@gmail.com',
    url='https://github.com/tinche/bower-cache',
    packages=[
        'registry',
    ],
    include_package_data=True,
    install_requires=[
        'Django==1.5',
        'djangorestframework==2.3.8',
        'envoy==0.0.2',
        'GitPython==0.3.2.RC1',
        'requests==2.0.0',
        'django-celery==3.0.23'
    ],
    license="MIT",
    zip_safe=False,
    keywords='bower',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
