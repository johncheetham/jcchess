#!/usr/bin/python

#
# start jcchess from within the source folder
#

import sys

assert sys.version_info >= (3,0)

import jcchess.gv

#sys.path.append("jcchess")
jcchess.gv.installed = False

import jcchess.jcchess
jcchess.jcchess.run()
