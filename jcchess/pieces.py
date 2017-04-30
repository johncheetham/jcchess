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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Rsvg
import os
import traceback
import chess

from . import gv

class Pieces:

    def __init__(self):
        self.pieceset = 1

    # called from jcchess.py
    def load_pieces(self, prefix):
        path = os.path.join(prefix, "images", "jcchess")
        p1 = self.load_pieceset(os.path.join(prefix, "images", "pieceset1"))
        p2 = self.load_pieceset(os.path.join(prefix, "images", "pieceset2"))
        self.piece_handles = (p1, p2)

    """
    def load_pieceset1(self):
        images = [
            "p", "n", "b", "r", "k", "q",
            "P", "N", "B", "R", "K", "Q",
            ]
        pieces = []

        for image in images:
            svg = chess.svg.piece(chess.Piece.from_symbol(image))
            svghandle = Rsvg.Handle.new_from_data(svg.encode())
            pieces.append(svghandle)
            #loader = GdkPixbuf.PixbufLoader()
            #loader.write(svg.encode())
            #loader.close()
            #pb = loader.get_pixbuf()
            #piece_pixbuf.append(pb)
        return pieces
    """

    def load_pieceset(self, pieces_dir):
        images = ["pawn", "knight", "bishop", "rook", "king", "queen"]
        pieces = []

        # Load pieces
        for side in ("B", "W"):
            for image in images:
                image = image + side + ".svg"
                path = os.path.join(pieces_dir, image)
                svghandle = Rsvg.Handle.new_from_file(path)
                pieces.append(svghandle)

        return pieces 

    def gethandle(self, piece): 
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
        return self.piece_handles[self.pieceset][idx-1]

    def get_pieceset(self):
        return self.pieceset

    def set_pieceset(self, pieceset):
        if pieceset not in (0,1):
            print("attempt to set invalid pieceset:",pieceset)
            return
        self.pieceset = pieceset

    def show_pieces_dialog(self, gtkaction):
        dialog = Gtk.Dialog(
            _("Select Pieces"), gv.gui.get_window(), 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        rb1 = Gtk.RadioButton.new_with_label(None, "Pieceset 1")
        dialog.vbox.pack_start(rb1, False, True, 5)
        rb2 = Gtk.RadioButton.new_with_label_from_widget(rb1, "Pieceset 2")
        dialog.vbox.pack_start(rb2, False, True, 5)
        dialog.show_all()
        dialog.set_default_response(Gtk.ResponseType.OK)
        if self.pieceset == 0:
            rb1.set_active(True)
        elif self.pieceset == 1:
            rb2.set_active(True)
        else:
            rb1.set_active()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            if rb1.get_active():
                self.pieceset = 0
            elif rb2.get_active():
                self.pieceset = 1
        dialog.destroy()
        return
