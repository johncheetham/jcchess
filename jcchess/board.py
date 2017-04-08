#
#   board.py
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
from gi.repository import GObject
from gi.repository import GdkPixbuf
from gi.repository import GLib
import cairo

import chess
import chess.pgn
from . import gv
from .constants import WHITE, BLACK

SCALE = 0.9      # scale the pieces so they occupy 90% of the board square
LINEWIDTH = 2    # width of lines on the board


class Board:

    def __init__(self):
        self.init_board()
        self.dnd = None        

    def init_board(self, fen="std"):
        if fen == "std":
            self.chessboard = chess.Board() # init board
        else:
            self.chessboard = chess.Board(fen)    
        
    def build_board(self):
        GObject.idle_add(self.update)

    # convert jcchess co-ordinates for square into
    # standard notation (e.g.  (1, 0) -> b1)
    def get_square_posn(self, x, y):
        lets = "abcdefghi"
        sq = lets[x] + str(y+1) 
        return sq

    # convert standard notation for square into
    # jcchess co-ordinates (e.g.  b1 -> (1, 0) )
    def get_gs_square_posn(self, sq):        
        lets = "abcdefgh"
        x = lets.index(sq[0:1])
        y = int(sq[1:2]) - 1
        return x, y

    def display_board(self):
        #
        # loop through the board squares and set the pieces
        # x, y = 0, 0 is the top left square of the board
        #
        for x in range(8):
            for y in range(8):
                gv.gui.get_event_box(x, y).queue_draw()

 
    #
    # test if user has clicked on a valid source square
    # i.e. one that contains a black piece if side to move is black
    #      otherwise white piece
    def valid_source_square(self, x, y, stm):
        piece = self.get_piece(x, y)
        pieces = [
            [
               "r", "n", "b", "q", "k", "p"
            ],
            [
                "R", "N", "B", "Q", "K", "P"
            ]
        ]

        try:
            idx = pieces[stm].index(piece)
        except ValueError as ve:
            return False

        return True

    def use_pieceset(self, pieceset):
        gv.pieces.set_pieceset(pieceset)
        self.refresh_screen()

    def update(self, refresh_gui=True):
        if refresh_gui:
            self.refresh_screen()

    def refresh_screen(self):
        self.display_board()

    #
    # return a pixbuf of the piece at the given square
    # used by drag_and_drop.py to get the drag and drop icon
    #
    def get_piece_pixbuf(self, x, y):
        # convert the x, y square to the location value used by the engine
        piece = self.get_piece(x, y)
        pb = gv.pieces.getpixbuf(piece)
        a = gv.gui.get_event_box(x, y).get_allocation()
        spb = pb.scale_simple(
            int(a.width*SCALE), int(a.height*SCALE), GdkPixbuf.InterpType.HYPER)
        return spb

    def get_piece_pixbuf_unscaled(self, x, y):
        # convert the x, y square to the location value used by the engine
        piece = self.get_piece(x, y)
        pb = gv.pieces.getpixbuf(piece)
        return pb

    #
    # called from jcchess.py to clear the source square when a drag of
    # a piece has started
    #
    def set_square_as_unoccupied(self, x, y):
        piece = "None"    # empty square
        self.dnd = (x, y)
        # redraw square
        GLib.idle_add(gv.gui.get_event_box(x, y).queue_draw)

    # called from gui.py when editing the board position to set the piece
    # on a square.
    def set_piece_at_square(self, x, y, piece, colour):
        self.chessboard.set_piece_at(chess.square(x, y), chess.Piece(piece, colour))       
        GLib.idle_add(gv.gui.get_event_box(x, y).queue_draw)
        
    # called from gui.py to remove piece during promotion dialog
    def remove_piece_at_square(self, x, y):
        piece=self.chessboard.remove_piece_at(chess.square(x, y))       
        GLib.idle_add(gv.gui.get_event_box(x, y).queue_draw)
        return piece

    # called when user does a "clear board" in board edit
    def clear_board(self):
        self.chessboard.clear()
        self.update()

    def set_image_cairo(self, x, y, cr=None, widget=None):
        piece = self.get_piece(x, y)

        if cr is None:
            w = gv.gui.get_event_box(x, y).get_window()
            cr = w.cairo_create()

        if widget is not None:
            a = widget.get_allocation()
        else:
            a = gv.gui.get_event_box(x, y).get_allocation()

        # if user has set hilite moves on then check if this square is
        # in last move and if so hilight it
        hilite = False
        if gv.gui.get_highlight_moves():
            try:
                lastmove = self.chessboard.peek()
            except IndexError:
                lastmove = ""
            if lastmove != "":
                sqnum = chess.square(x, y)
                if sqnum in (lastmove.from_square, lastmove.to_square):
                    hilite = True

        # clear square to square colour
        #gv.set_board_colours.set_square_colour(cr, a, LINEWIDTH, hilite)
        # FIXME - hard coded colours
        if (x+y) % 2 == 0:
            #r, g, b = self.get_cairo_colour(square_colour)
            r, g, b = 205/255, 133/255,  63/255
        else:
            #r, g, b = 1, 1, 1
            r, g, b = 255/255, 222/255, 173/255
        # modify it a bit to get r, g, b of hilite colour
        #if hilite:
        #    r -= 50/255
        #    g -= 50/255
        #    b -= 50/255
        
        if hilite:
            cr.set_source_rgb(1, 0, 0)
            cr.rectangle(1, 1 , a.width, a.height)
            cr.fill()
            cr.set_source_rgb(r, g, b)
            cr.rectangle(3, 3, a.width-6, a.height-6)
            cr.fill()
        else:
            cr.set_source_rgb(r, g, b)
            cr.rectangle(1, 1 , a.width-LINEWIDTH, a.height-LINEWIDTH)
            cr.fill()
        
        # set offset so piece is centered in the square
        cr.translate(a.width*(1.0-SCALE)/2.0, a.height*(1.0-SCALE)/2.0)

        # scale piece so it is smaller than the square
        if self.dnd is not None and self.dnd == (x, y):
            pb = gv.pieces.getpixbuf("None")
            self.dnd = None
        else:    
            pb = self.get_piece_pixbuf_unscaled(x, y)
        sfw = (a.width * 1.0 / pb.get_width()) * SCALE
        sfh = (a.height * 1.0 / pb.get_height()) * SCALE
        cr.scale(sfw, sfh)

        Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
        cr.paint()

    def get_piece(self, x, y):
        piece = self.chessboard.piece_at(chess.square(x, y))
        piece = str(piece)   
        return piece

    def get_legal_moves(self):
        return self.chessboard.legal_moves
        
    def add_move(self, cmove):    
        self.chessboard.push(cmove)
        
    def remove_move(self):
        self.chessboard.pop()
        
    def print_board(self):
        print("board fen:",repr(self.chessboard))
        print("board:\n",self.chessboard)
        
    def is_gameover(self):
        if self.chessboard.is_game_over():
            return True
        else:
            return False
                
    #def is_checkmate(self):
    #    if self.chessboard.is_checkmate():
    #        return True
    #    else:
    #        return False
            
    def parse_san(self, move):
        return self.chessboard.parse_san(move)
        
    def get_game(self):
        game = chess.pgn.Game.from_board(self.chessboard)         
        del game.headers["Event"]
        del game.headers["Site"]
        del game.headers["Date"]
        del game.headers["Round"]
        game.headers["White"] = gv.jcchess.get_player(WHITE)
        game.headers["Black"] = gv.jcchess.get_player(BLACK)
        return game
        
    def get_fen(self):
        return self.chessboard.fen()
                
