import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

import os
import sys
import shutil

import jcchess.constants

assert sys.version_info >= (3,0)

VERSION = jcchess.constants.VERSION

# linux
data_files=[
  (sys.prefix+'/share/applications',['jcchess.desktop']),
  (sys.prefix+'/share/pixmaps', ['jcchess.png'])]

package_data_list = []

# translations
if shutil.which("msgfmt") is None:
    print("msgfmt not found. Translations will not be built")
else:
    localedir = "locale"
    dirlist = os.listdir(localedir)
    for d in dirlist:
        pth = os.path.join(localedir, d)
        if not os.path.isdir(pth):
            continue
        filein = os.path.join(pth, "LC_MESSAGES", "jcchess.po")
        pthout = os.path.join("jcchess", pth, "LC_MESSAGES")
        if not os.path.exists(pthout):
            try:
                os.makedirs(pthout)
            except OSError as exc:
                print("Unable to create locale folder", pthout)
                sys.exit()
        fileout = os.path.join(pthout, "jcchess.mo")
        os.popen("msgfmt %s -o %s" % (filein, fileout))
        package_data_list.append(os.path.join(pth, "LC_MESSAGES", "jcchess.mo"))

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="jcchess",
      version=VERSION,
      description="A Chess GUI", 
      include_package_data=True,
      author="John Cheetham",
      author_email="developer@johncheetham.com",
      url="http://www.johncheetham.com/projects/jcchess/",
      long_description=read("README.rst"),
      platforms=["Linux"],
      license="GPLv3+",
      zip_safe=False,

      packages=["jcchess"],
      package_data={
          "jcchess": package_data_list,
      },
      data_files=data_files,
      entry_points={
          "gui_scripts": [
              "jcchess = jcchess.jcchess:run",
          ]
      },

      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: X11 Applications :: GTK",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: C",
          "Topic :: Games/Entertainment :: Board Games",
          ],

      )
