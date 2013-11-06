# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

import registry

from setuptools import setup
from setuptools.command.test import test as TestCommand

VERSION = registry.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print(" git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    print(" git push --tags")
    sys.exit()

readme = open('README.md').read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


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
        'Django >= 1.5, < 1.6',
        'djangorestframework==2.3.8',
        'envoy==0.0.2',
        'GitPython==0.3.2.RC1',
        'requests==2.0.0',
        'django-celery==3.0.23'
    ],
    tests_require=[
        'pytest-django',
    ],
    cmdclass={'test': PyTest},
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
