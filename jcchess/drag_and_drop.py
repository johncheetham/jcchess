#
#   drag_and_drop.py
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
from gi.repository import GObject
import cairo

from .constants import TARGET_TYPE_TEXT
from . import gv
from .board import SCALE

class Drag_And_Drop:

    drag_and_drop_ref = None

    #
    # user has begun to drag a piece
    #
    def drag_begin(self, widget, drag_context, data):

        self.dnd_data_received = False

        # get x,y co-ords of source square
        x, y = data

        if gv.verbose:
            print("in drag begin")
            print("data=", data)
            print("widget_name=", widget.get_name())
            print("source sq=", x, y)

        stm = gv.jcchess.get_side_to_move()

        # convert the x, y co-ords into the shogi representation
        # (e.g. 8, 6 is 1g)
        sq = gv.board.get_square_posn(x, y)

        self.src = sq
        if gv.verbose:
            print("source square: (x, y) = (", x, ",",  y, ") ", sq)
        self.src_x = x
        self.src_y = y

        # set the icon for the drag and drop to the piece that is being
        # dragged
        self.piece = gv.board.get_piece(x, y)
        # get width/height of board square
        a = gv.gui.get_event_box(x, y).get_allocation()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, a.width, a.height)
        svghandle = gv.board.get_piece_handle(x, y)
        dim = svghandle.get_dimensions()

        cr = cairo.Context(surface)
        sfw = (a.width * 1.0 / dim.width) * SCALE
        sfh = (a.height * 1.0 / dim.height) * SCALE
        cr.scale(sfw, sfh)

        svghandle.render_cairo(cr)
        # set mouse pointer to be in middle of drag icon
        surface.set_device_offset(-a.width/2, -a.height/2)
        Gtk.drag_set_icon_surface(drag_context, surface)

        # clear the square where the piece is being moved from
        gv.board.set_square_as_unoccupied(x, y)

    def sendCallback(self, widget, context, selection, targetType, eventTime):
        if targetType == TARGET_TYPE_TEXT:
            sel = "jcchess"
            selection.set_text(sel, 8)

    def receiveCallback(self, widget, context, x, y, selection, targetType,
                        time, data):
        if gv.verbose:
            print("in receive callback")
            print("x=", x)
            print("y=", y)
            print("selection.data=", selection.get_text())
            print("targetType=", targetType)
            print("time=", time)
            print("data=", data)

        self.dnd_data_received = True

        # get x,y co-ords of dest square
        x, y = data

        # convert the x, y co-ords into the shogi representation
        # (e.g. 8, 6 is 1g)
        sq = gv.board.get_square_posn(x, y)

        # set destination square
        dst = sq
        if gv.verbose:
            print("dst =", dst)

        move = gv.jcchess.get_move(self.piece, self.src, dst, self.src_x,
                                  self.src_y, x, y)
        if gv.verbose:
            print("move=", move)
            print()

        # if drag and drop failed then reinstate the piece where it
        # was dragged from
        if move is None:
            gv.board.update()
            return

        # display the move
        GObject.idle_add(gv.jcchess.human_move, move)

    # if drag and drop failed then reinstate the piece where it
    # was dragged from
    def drag_end(self, widget, drag_context):
        # if receiveCallback function not entered then restore board
        # to before the drag started
        if not self.dnd_data_received:
            gv.board.update()
            return


def get_ref():
    if Drag_And_Drop.drag_and_drop_ref is None:
        Drag_And_Drop.drag_and_drop_ref = Drag_And_Drop()
    return Drag_And_Drop.drag_and_drop_ref
