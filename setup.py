#!/usr/bin/env python

from distutils.core import setup
import sys
VERSION = '0.1.7'
DESC = 'Native Python Barobo robotics control library'
AUTHOR = 'David Ko'
AUTHOR_EMAIL = 'david@barobo.com'
MAINTAINER = 'David Ko'
MAINTAINER_EMAIL = 'david@barobo.com'
URL = 'http://www.barobo.com'

if sys.platform == "win32":
  print('Building for WIN32')
  setup(name='PyBarobo',
      version=VERSION,
      description=DESC,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=URL,
      license='GPL',
      platforms='any',
      packages=['barobo'],
      package_dir={'barobo': 'barobo'},
      package_data={'barobo': ['lib/*.dll']}
      #py_modules=['pybarobo']
      )

else:
  setup(name='PyBarobo',
      version=VERSION,
      description=DESC,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=URL,
      license='GPL',
      platforms='any',
      packages=['barobo']
      #py_modules=['pybarobo']
      )
