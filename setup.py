# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


VERSION = '0.4.2'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print(" git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    print(" git push --tags")
    sys.exit()

with open('README.md') as f: readme = f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test_bowercache']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


class Coverage(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test_bowercache']
        self.test_suite = True

    def run_tests(self):
        import coverage
        import pytest
        cov = coverage.coverage()
        cov.start()
        errno = pytest.main(self.test_args)
        cov.stop()
        cov.save()
        cov.report()
        sys.exit(errno)

install_requires = [
    'django-bower-cache==0.4.2',
    'django-celery==3.1.16',
    'dj-static==0.0.6',
    'gunicorn==19.1.1',
]

tests_require = [
    'pytest-django',
    'coverage',
    'beautifulsoup4',
]

if sys.version_info[0] == 2:
    tests_require.append('mock==1.0.1')

setup(
    name='bower-cache',
    version=VERSION,
    description='A local caching proxy for Bower packages.',
    long_description=readme + '\n\n',
    author='Tin Tvrtkovic',
    author_email='tinchester@gmail.com',
    url='https://github.com/tinche/bower-cache',
    packages=['bowercache'],
    entry_points={
        'console_scripts': ['bower-cache-init = bowercache:init_site'],
    },
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        ':python_version=="2.6"': ['importlib'],
    },
    cmdclass={'test': PyTest, 'coverage': Coverage},
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
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
