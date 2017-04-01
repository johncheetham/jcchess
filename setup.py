import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension

import os
import platform
import sys
import string
import shutil

import jcchess.constants

assert sys.version_info >= (3,0)

VERSION = jcchess.constants.VERSION

if (sys.argv[1] == "install"):
    if (not os.path.exists("jcchess/data/opening.bbk")):
        print("warning - opening book not found")
        print("you must run 'python setup.py build' first to build the " \
              "opening book")
        sys.exit()

macros = [
        ("HAVE_BCOPY", "1"),
        ("HAVE_ERRNO_H", "1"),
        ("HAVE_FCNTL_H", "1"),
        ("HAVE_MEMCPY", "1"),
        ("HAVE_MEMSET", "1"),
        ("HAVE_SETLINEBUF", "1"),
        ]

if os.name == "nt":
    # windows
    macros.append(("HASHFILE", "1"))
    data_files=[]
else:
    # linux
    macros.append(("HAVE_UNISTD_H", "1"))
    macros.append(("HASHFILE", "\"data/gnushogi.hsh\""))
    data_files=[
      (sys.prefix+'/share/applications',['jcchess.desktop']),
      (sys.prefix+'/share/pixmaps', ['jcchess.png'])]

package_data_list = ["data/opening.bbk"]

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

if (sys.argv[1] != "build"):
    sys.exit()

#
# build the opening book
#

def get_plat():
    if os.name == 'nt':
        prefix = " bit ("
        i = sys.version.find(prefix)
        if i == -1:
            return sys.platform
        j = sys.version.find(")", i)
        look = sys.version[i+len(prefix):j].lower()
        if look == 'amd64':
            return 'win-amd64'
        if look == 'itanium':
            return 'win-ia64'
        return sys.platform

    # linux
    (osname, host, release, version, machine) = os.uname()
    osname = osname.lower()
    osname = osname.replace("/", "")
    machine = machine.replace(" ", "_")
    machine = machine.replace("/", "-")
    if osname[:5] != "linux":
        print("OS not supported")
    plat_name = "%s-%s" % (osname, machine)
    return plat_name

plat_name = get_plat()
plat_specifier = ".%s-%s" % (plat_name, sys.version[0:3])
build_lib = "lib" + plat_specifier
pypath = os.path.join("build", build_lib, "jcchess")
sys.path.append(pypath)
