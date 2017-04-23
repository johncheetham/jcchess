#
#   utils.py
#
#   This file is part of jcchess
#
#   jcchess is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   jcchess is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with jcchess.  If not, see <http://www.gnu.org/licenses/>.
#

from gi.repository import Gtk
from gi.repository import Gdk
import os
import sys
import pickle
import chess
import chess.pgn
from io import StringIO

from . import load_save
from . import gv
from .constants import VERSION


# Copy the board position to the clipboard in std FEN format
def copy_FEN_to_clipboard(action):
    fen = gv.board.get_fen()
    copy_text_to_clipboard(fen)


# paste a position from the clipboard
def paste_clipboard_to_FEN(action):
    fen = get_text_from_clipboard()
    if fen is None:
        gv.gui.info_box("Error: invalid fen")
        return
        
    # check the fen is valid    
    try:
        chessboard = chess.Board(fen)
    except ValueError as ve:
        print("Error - Pasted fen invalid: "+str(ve))
        print("Error - FEN data:",fen) 
        gv.gui.info_box("Error: invalid fen")
        return
    gv.load_save.init_game(fen)
    

def copy_game_to_clipboard(action):
    copy_text_to_clipboard(str(gv.board.get_game()))


def paste_game_from_clipboard(action):
    gamestr = get_text_from_clipboard()
    if gamestr is None:
        print("Error invalid game data")
        return
    pgn = StringIO(gamestr)
    game = chess.pgn.read_game(pgn)
    gv.load_save.load_game_pgn(game)

    
def copy_text_to_clipboard(text):
    # get the clipboard
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    # put the FEN data on the clipboard
    clipboard.set_text(text, -1)
    # make our data available to other applications
    clipboard.store()


def get_text_from_clipboard():
    # get the clipboard
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    # read the text from the clipboard
    text = clipboard.wait_for_text()
    return text


def get_settings_from_file(filepath):
    s = None
    try:
        settings_file = os.path.join(filepath, "settings")
        f = open(settings_file, "rb")
        s = pickle.load(f)
        f.close()
    except EOFError as eofe:
        print("eof error:", eofe)
    except pickle.PickleError as pe:
        print("pickle error:", pe)
    except IOError as ioe:
        # Normally this error means it is the 1st run and the settings file
        # does not exist
        pass
    except Exception as exc:
        print("Cannot restore settings:", exc)
    #if gv.verbose:
    #    print "values read from settings file"
    #    print "colour_settings:",s.colour_settings
    return s


def get_prefix():
    # prefix to find package files/folders
    prefix = os.path.abspath(os.path.dirname(__file__))
    if gv.verbose:
        print("base directory (prefix) =", prefix)
    return prefix


def create_settings_dir():
    # set up jcchess directory under home directory
    home = os.path.expanduser("~")
    jcchesspath = os.path.join(home, ".jcchess")
    if not os.path.exists(jcchesspath):
        try:
            os.makedirs(jcchesspath)
        except OSError as exc:
            raise
    return jcchesspath


def get_verbose():
    verbose = False
    verbose_uci = False
    showmoves = False
    showheader = False
    for arg in sys.argv:
        if arg == "-v" or arg == "--verbose":
            verbose = True
        if arg == "-vuci":
            verbose_uci = True
        if arg == "-m":
            showmoves = True
        if arg == "-h":
            showheader = True
        if arg == "-mh" or arg == "-hm":
            showmoves = True
            showheader = True           
    return verbose, verbose_uci, showmoves, showheader
