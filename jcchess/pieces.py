#
#   pieces.py
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

from gi.repository import Gdk
from gi.repository import GdkPixbuf
import os
import traceback
import chess


class Pieces:

    def __init__(self):
        self.pieceset = "jcchess"     # jcchess, eastern, western or custom
        self.custom_piece_pixbuf = None
        self.custom_piece_path = None

        # create pixbuf for empty square
        self.pb_empty = GdkPixbuf.Pixbuf.new(
            GdkPixbuf.Colorspace.RGB, True, 8, 64, 64)
        self.pb_empty.fill(0xffffff00)  # fill with transparent white

    # called from jcchess.py
    def load_pieces(self, prefix):
        #  0 - unoccupied
        #  1 - black pawn
        #  2 - black lance
        #  3 - black knight
        #  4 - black silver general
        #  5 - black gold general
        #  6 - black bishop
        #  7 - black rook
        #  8 - black king
        #  9 - promoted black pawn
        # 10 - promoted black lance
        # 11 - promoted black knight
        # 12 - promoted black silver general
        # 13 - promoted black bishop
        # 14 - promoted black rook
        # 15 - white pawn
        # 16 - white lance
        # 17 - white knight
        # 18 - white silver general
        # 19 - white gold general
        # 20 - white bishop
        # 21 - white rook
        # 22 - white king
        # 23 - promoted white pawn
        # 24 - promoted white lance
        # 25 - promoted white knight
        # 26 - promoted white silver general
        # 27 - promoted white bishop
        # 28 - promoted white rook

        # load builtin jcchess pieces as pixbufs
        path = os.path.join(prefix, "images", "jcchess")
        self.jcchess_piece_pixbuf, errmsg = self.load_pixbufs(path)
        if errmsg is not None:
            print("Error loading jcchess pieces:",errmsg)
            return 1

        # load builtin gnushogi eastern pieces as pixbufs
        #path = os.path.join(prefix, "images", "eastern")
        #self.eastern_piece_pixbuf, errmsg = self.load_pixbufs(path)
        #if errmsg is not None:
        #    print("Error loading eastern pieces:",errmsg)
        #    return 1

        # load builtin gnushogi western pieces as pixbufs
        #path = os.path.join(prefix, "images", "western")
        #self.western_piece_pixbuf, errmsg = self.load_pixbufs(path)
        #if errmsg is not None:
        #    print("Error loading western pieces:",errmsg)
        #    return 1

        # load custom piece pixbufs if any
        if self.custom_piece_path is not None:
            self.custom_piece_pixbuf, errmsg =  self.load_pixbufs(
                self.custom_piece_path)
            # if pieces set to custom and they cannot be loaded then switch to
            # eastern
            if self.custom_piece_pixbuf is None:
                if errmsg is not None:
                    print(errmsg)
                if self.pieceset == "custom":
                    self.pieceset = "jcchess"

    def custom_pieces_loaded(self):
        if self.custom_piece_pixbuf is not None:
            return True
        else:
            return False

    # method to load images of pieces
    def load_pixbufs(self, pieces_dir):
        images = [
            "pawn", "knight",
            "bishop", "rook", "king", "queen",
            ]        

        piece_pixbuf = []
        # first pixbuf in list is empty square
        piece_pixbuf.append(self.pb_empty.copy())

        # get file extension (png or svg)
        image = images[0] + "B"
        if os.path.isfile(os.path.join(pieces_dir, image + ".png")):
            extension = ".png"
        elif os.path.isfile(os.path.join(pieces_dir, image + ".svg")):
            extension = ".svg"
        else:
            return None, "Error loading pieces\n\nFile not " \
                        "found:pawnB.png or pawnB.svg"

        # Load black pieces
        for image in images:
            # custom pieces
            image = image + "B"+ extension
            path = os.path.join(pieces_dir, image)
            if not os.path.isfile(path):
                errmsg = "Error loading pieces\nFile not found:" + image
                return None, errmsg
            pb = GdkPixbuf.Pixbuf.new_from_file(path)
            piece_pixbuf.append(pb)

        # Load white pieces
        for image in images:
            # change filename from pawnB to pawnW etc
            image_white = image + "W" + extension

            # if user has provided an image for white then use it
            path = os.path.join(pieces_dir, image_white)
            if os.path.isfile(path):
                pb = GdkPixbuf.Pixbuf.new_from_file(path)
                piece_pixbuf.append(pb)
                continue

            # no image provided for white so use the image for black and
            # rotate it through 180 degrees
            image = image + "B" + extension
            path = os.path.join(pieces_dir, image)

            pb = GdkPixbuf.Pixbuf.new_from_file(path)
            pb = pb.rotate_simple(GdkPixbuf.PixbufRotation.UPSIDEDOWN)
            piece_pixbuf.append(pb)

        return piece_pixbuf, None

    # called from set_board_colours.py when user loads new custom pieces
    def load_custom_pieces(self, path):
        custom_piece_pixbufs, errmsg = self.load_pixbufs(path)
        # if no errors then set custom pixbufs to the new set
        if errmsg is None:
            self.custom_piece_pixbuf = custom_piece_pixbufs
            self.custom_piece_path = path
        return errmsg

    def getpixbuf(self, piece):
        #print(piece.color,piece.piece_type)
        #piece = piece.symbol()
        #if piece==
        # pieces contains the list of possible pieces
        pieces = [
            "None", "p", "n", "b", "r", "k", "q",
                  "P", "N", "B", "R", "K", "Q"]

        try:
            idx = pieces.index(piece)
        except ValueError as ve:
            traceback.print_exc()
            print("error piece not found, piece =", piece)
            print(len(piece))

        if self.pieceset == "jcchess":
            pixbuf = self.jcchess_piece_pixbuf[idx]
        elif self.pieceset == "eastern":
            pixbuf = self.eastern_piece_pixbuf[idx]
        elif self.pieceset == "western":
            pixbuf = self.western_piece_pixbuf[idx]
        elif self.pieceset == "custom":
            try:
                pixbuf = self.custom_piece_pixbuf[idx]
            except TypeError as te:
                print("error loading custom pieces", te)
                pixbuf = self.jcchess_piece_pixbuf[idx]
                self.pieceset = "jcchess"
        else:
            print("invalid pieceset in getpixbuf in pieces.py:", self.pieceset)
            self.pieceset = "jcchess"
            pixbuf = self.jcchess_piece_pixbuf[idx]   # default to jcchess pieces
        return pixbuf

    def get_pieceset(self):
        return self.pieceset

    def set_pieceset(self, pieceset):
        self.pieceset = pieceset

    def get_custom_pieceset_path(self):
        return self.custom_piece_path

    def set_custom_pieceset_path(self, path):
        self.custom_piece_path = path
