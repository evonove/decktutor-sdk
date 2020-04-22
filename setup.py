# -*- coding: utf-8 -*-
#!/usr/bin/env python

import sys, os
from setuptools import setup
from decktutorsdk.version import __version__

version = __version__

setup(
  name='decktutorsdk',
  version= __version__,
  author='Evonove',
  author_email='dev@evonove.it',
  packages=['decktutorsdk'],
  scripts=[],
  url='https://evonove.it',
  license='MIT',
  description='Decktutor base sdk.',
  long_description="""
    Decktutor sdk with use of some endpoints.
  """,
  install_requires=['requests', 'six'],
  classifiers=[
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Topic :: Software Development :: Libraries :: Python Modules'
  ],
  keywords="decktutor sdk",
)
