JCchess - John Cheetham - http://www.johncheetham.com/projects/jcchess
 
Description
-----------
JCchess is a program to play chess against UCI chess engines.

Requirements
------------
python3 python-cairo python-gobject

Package names to install.

================== = ================================
distro             : packages
================== = ================================
Debian/Mint/Ubuntu : python3-gi-cairo gir1.2-rsvg-2.0
Fedora             : python3-cairo, python3-gobject
Arch               : python-cairo, python-gobject
================== = ================================

Usage
-----
Enter 'python3 run.py' to start the program.
Alternatively you can install it on your system with 'python3 setup.py install'
(as root user) and then start it from the gui menu or by entering 'jcchess' into
a terminal.
Windows versions are available on the website.

Adding a UCI engine
-------------------
To add an engine to play against click on Options, engines then click
the 'Add' button to add a new engine. Navigate to the engine executable
and add it. Then click the OK button.

Next do Options, players and set the black player to the new engine.

Click on the 'tick' button at the top of the screen to start the game 
and then move a white piece.

For debugging start with -v (all debugging messages) or -vuci (uci
messages).

Acknowledgements
----------------
The initial version was based on gshogi.
see http://www.johncheetham.com/projects/gshogi

python-chess is used.
see https://github.com/niklasf/python-chess

Piece Images by DG-RA
see https://openclipart.org/user-detail/DG-RA
