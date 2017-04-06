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
        #self.chessboard = chess.Board()
        #print("self.chessboard=\n",self.chessboard)
        #print(" ")
        self.init_board()
        self.board_position = self.getboard()        
        
        #self.board_array= [[' ' for x in range(8)] for y in range(8)]
        #print("self.board_position=",self.board_position)
        #self.board_position= [' l', ' n', ' s', ' g', ' k', ' g', ' s', ' n', ' l', ' -', ' b', ' -', ' -', ' -', ' -', ' -', ' r', ' -', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' -', ' R', ' -', ' -', ' -', ' -', ' -', ' B', ' -', ' L', ' N', ' S', ' G', ' K', ' G', ' S', ' N', ' L']
        #print("len=",len(self.board_position))
        #self.board_position= [' r', ' n', ' b', ' q', ' k', ' b', ' n', ' r', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' R', ' N', ' B', ' Q', ' K', ' B', ' N', ' R']        
        #print("len=",len(self.board_position))
        self.dnd = None        

    def init_board(self, fen="std"):
        if fen == "std":
            self.chessboard = chess.Board() # init board
        else:
            self.chessboard = chess.Board(fen)    
        
    def build_board(self):
        GObject.idle_add(self.update)

    def get_gs_loc(self, x, y):
        #l = x + (8 - y) * 9
        l = x + (7 - y) * 8
        #l = x + y * 8
        return l

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

    #
    # USI SFEN string
    #
    # uppercase letters for black pieces, lowercase letters for white pieces
    #
    # examples:
    #     "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1"
    #     "8l/1l+R2P3/p2pBG1pp/kps1p4/Nn1P2G2/P1P1P2PP/1PS6/1KSG3+r1/LN2+p3L w
    # Sbgn3p 124"
    def get_sfen(self):

        empty = 0
        sfen = ""

        # board state
        for y in range(8):
            for x in range(8):
                # convert the x, y square to the location value
                # used by the engine
                l = self.get_gs_loc(x, y)
                p = self.board_position[l]
                if p == " -":
                    empty += 1
                    continue
                if empty != 0:
                    sfen += str(empty)
                    empty = 0
                if p[1].isupper():
                    usi_p = p[1].lower()
                else:
                    usi_p = p[1].upper()
                if p[0] == "+":
                    usi_p = "+" + usi_p
                sfen += usi_p
            if empty != 0:
                sfen += str(empty)
                empty = 0
            if y != 8:
                sfen += "/"

        # side to move
        if gv.jcchess.get_stm() == BLACK:
            stm = "b"
        else:
            stm = "w"
        sfen = sfen + " " + stm

        # pieces in hand
        pih = ""

        # get list of captured pieces for black in the correct order
        # (rook, bishop, gold, silver, knight, lance, pawn)
        cap_list = []
        for p in ("R", "B", "G", "S", "N", "L", "P"):
            zcap = self.getcap(p, self.cap[BLACK])
            if zcap != "":
                cap_list.append(zcap)

        # get list captured pieces for white in the correct order
        # (rook, bishop, gold, silver, knight, lance, pawn)
        for p in ("R", "B", "G", "S", "N", "L", "P"):
            zcap = self.getcap(p, self.cap[WHITE])
            if zcap != "":
                # change to lower case for white
                zcap2 = zcap[0] + zcap[1].lower()
                cap_list.append(zcap2)

        # cap_list is now a list of captured pieces in the correct order
        # (black R, B, G, S, N, L, P followed by white R, B, G, S, N, L, P)

        # create pices in hand string (pih) from cap_list
        for c in cap_list:
            piece = c[1:2]
            num = c[0:1]
            if int(num) > 1:
                pih += str(num)
            pih += piece

        if pih == "":
            pih = "-"

        move_count = gv.jcchess.get_move_count()
        sfen = sfen + " " + pih + " " + str(move_count)
        return sfen

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

    #
    def valid_source_square(self, x, y, stm):
        #l = self.get_gs_loc(x, y)
        #piece = self.board_position[l]
        piece = self.get_piece(x, y)
        #print("jjjpiece=",x,y,piece)
        #print("piece=",piece)
        #print("stm=",stm)
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

#
# Check if promotion is mandatory (i.e on last rank of board for
# pawn/lance or last 2 ranks for knight) or optional
#
# return
# 0 - no promotion
# 1 - promotion optional
# 2 - promotion mandatory
#
    def promote(self, piece, src_x, src_y, dst_x, dst_y, stm):

        # check for mandatory
        if stm == BLACK:
            if (dst_y == 0):
                if (piece == " p" or piece == " l" or piece == " n"):
                    return 2
            elif (dst_y == 1):
                if (piece == " n"):
                    return 2
        else:
            if (dst_y == 8):
                if (piece == " P" or piece == " L" or piece == " N"):
                    return 2
            elif (dst_y == 7):
                if (piece == " N"):
                    return 2

        # check for optional
        #        BlackPawn,    BlackLance,   BlackKnight, BlackSilver,
        #        BlackBishop,  BlackRook,
        promotable_pieces = [
            [
                " p", " l", " n", " s", " b", " r"
            ],
            [
                " P", " L", " N", " S", " B", " R"
            ]
        ]

        try:
            idx = promotable_pieces[stm].index(piece)
        except ValueError as ve:
            return 0

        return 1

    def use_pieceset(self, pieceset):
        gv.pieces.set_pieceset(pieceset)
        self.refresh_screen()

    def getboard(self):
        
        b = []
        
        for x in self.chessboard.fen(): 
            """
            if x == "R":
                b.append(' r')
            elif  x == "N":
                b.append(' n')
            elif x == "B":
                b.append(' b')
            elif  x == "Q":
                b.append(' q')
            elif  x == "K":
                b.append(' k')
            elif  x == "P":
                b.append(' p')
            elif x == "r":
                b.append(' R')
            elif  x == "n":
                b.append(' N')
            elif x == "b":
                b.append(' B')
            elif  x == "q":
                b.append(' Q')
            elif  x == "k":
                b.append(' K')
            elif  x == "p":
                b.append(' P')
            elif x.isdigit():
                for y in range(int(x)):
                    b.append(' -')
            elif x == " ":
                break
            
            """
            if x == "R":
                b.append(' R')
            elif  x == "N":
                b.append(' N')
            elif x == "B":
                b.append(' B')
            elif  x == "Q":
                b.append(' Q')
            elif  x == "K":
                b.append(' K')
            elif  x == "P":
                b.append(' P')
            elif x == "r":
                b.append(' r')
            elif  x == "n":
                b.append(' n')
            elif x == "b":
                b.append(' b')
            elif  x == "q":
                b.append(' q')
            elif  x == "k":
                b.append(' k')
            elif  x == "p":
                b.append(' p')
            elif x.isdigit():
                for y in range(int(x)):
                    b.append(' -')
            elif x == " ":
                break  
                  
        #print("b=",b)
        if len(b) != 64:
            print("Length error in getboard")                    
        #return [' r', ' n', ' b', ' q', ' k', ' b', ' n', ' r', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' R', ' N', ' B', ' Q', ' K', ' B', ' N', ' R'] 
        #print([' R', ' N', ' B', ' Q', ' K', ' B', ' N', ' R', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' P', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' -', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' p', ' r', ' n', ' b', ' q', ' k', ' b', ' n', ' r']       )
        #return engine.getboard()
        return b

    def update(self, refresh_gui=True):
        self.board_position = self.getboard()
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
        #l = self.get_gs_loc(x, y)
        #piece = self.board_position[l]
        piece = self.get_piece(x, y)
        pb = gv.pieces.getpixbuf(piece)
        a = gv.gui.get_event_box(x, y).get_allocation()
        spb = pb.scale_simple(
            int(a.width*SCALE), int(a.height*SCALE), GdkPixbuf.InterpType.HYPER)
        return spb

    def get_piece_pixbuf_unscaled(self, x, y):
        # convert the x, y square to the location value used by the engine
        l = self.get_gs_loc(x, y)                
        #piece = self.board_position[l]
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
        print("pppiece=",piece)
        #self.chessboard.set_piece_at(square, piece, promoted=False)
        self.chessboard.set_piece_at(chess.square(x, y), chess.Piece(piece, colour))
        print("pieceat=",self.chessboard.piece_at(chess.square(x, y)))
        #l = self.get_gs_loc(x, y)
        #self.board_position = self.getboard()
        #self.board_position[l] = piece
        #self.update()        
        GLib.idle_add(gv.gui.get_event_box(x, y).queue_draw)

    # called when user does a "clear board" in board edit
    def clear_board(self):
        self.chessboard.clear()
        self.update()
        #for x in range(8):
        #    for y in range(8):
        #        self.set_square_as_unoccupied(x, y)

    def set_image_cairo(self, x, y, cr=None, widget=None):
        piece = self.get_piece(x, y)
        #print("xxxxxxxx,y=",x,y,piece)

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
                #print(lastmove.from_square)
            except IndexError:
                lastmove = ""                
            #lastmove = gv.jcchess.get_lastmove()
            if lastmove != "":
                sqnum = chess.square(x, y)
                if sqnum in (lastmove.from_square, lastmove.to_square):
                    hilite = True 
                #lets = "abcdefgh"
                #nums = "12345678"
                #lastsrc = (lets.index(lastmove[0]), nums.index(lastmove[1]))
                #lastdst = (lets.index(lastmove[2]), nums.index(lastmove[3])) 
                #if (x, y) in (lastsrc, lastdst):
                #    hilite = True
                #    print("hilite true")
                #movesquares = []
                #src = lastmove[0:2]
                #dst = lastmove[2:4]
                #if src[1] != "*":
                #    movesquares.append(self.get_gs_square_posn(lastmove[0:2]))
                #movesquares.append(self.get_gs_square_posn(lastmove[2:4]))
                #if (x, y) in movesquares:
                #    hilite = True

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
        #l = self.get_gs_loc(x, y)
        #piece = self.board_position[l]
        #print("x,yyyyy=",x,y,piece)
        piece = self.chessboard.piece_at(chess.square(x, y))
        #if piece == None:
        #    piece = " "
        #else:
        #    piece = str(piece) 
        piece = str(piece)   
        return piece

    def get_legal_moves(self):
        return self.chessboard.legal_moves
        
    def add_move(self, cmove):    
        self.chessboard.push(cmove)
        
    def remove_move(self):
        self.chessboard.pop()
        
    def print_board(self):
        #engine.command("bd")
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
            
    #def get_board(self):
    #    return self.chessboard                

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
                
