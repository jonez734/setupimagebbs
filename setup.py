#!/usr/bin/env python

from distutils.core import setup

import time

r = 1
v = time.strftime("%Y%m%d%H%M")

projectname = "empyre"

setup(
  name=projectname,
  version=v,
  url="https://repo.zoidtechnologies.com/%s/" % (projectname),
  author="zoid technologies",
  author_email="%s@projects.zoidtechnologies.com" % (projectname),
  py_modules=["empyre"],
  requires=["ttyio4", "bbsengine4"],
  scripts=["empyre"],
  license="GPLv2",
  provides=[projectname],
  classifiers=[
    "Programming Language :: Python :: 3.7",
    "Environment :: Console",
    "Development Status :: 4 - Beta",
    "Intended Audience :: End Users",
    "Operating System :: POSIX",
    "Topic :: Terminals",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Topic :: Communications :: BBS"
  ],
  long_description = """empyre -- turn-based strategy game built upon bbsengine4""",
  command_options = {
    "build_sphinx": {
      "project": projectname,
      "version": v,
      "release": r,
      "source_dir": ( "setup.py", "doc/" )
    }
  }
)
