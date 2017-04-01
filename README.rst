JCchess - John Cheetham - http://www.johncheetham.com/projects/jcchess
 
Description
-----------
JCchess is a program to play chess against UCI chess engines.

Requirements
------------
python3 python-cairo python-gobject gtk3

Usage
-----
Enter 'python3 run.py' to start the program.

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
