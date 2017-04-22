#
#   set_board_colours.py - Gui Dialog to Change the Bopard Colours
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
import cairo
import os

from . import gv


class Set_Board_Colours:

    BROWN, BLUE, GREEN = range(3)

    def __init__(self, prefix):
        if gv.verbose:
            print("in set_board_colours - init")
        self.colour_scheme = Set_Board_Colours.BROWN
        if gv.verbose:
            print("colour scheme set to default:", self.colour_scheme)
        # wood texture for border
        path = os.path.join(prefix, "images", "wood1.png")
        self.wood1 = cairo.ImageSurface.create_from_png(path)

    def set_colour_scheme(self, colour_scheme):
        if gv.verbose:
            print("in set_board_colours - set_colour_scheme")
            print("colour_scheme=", colour_scheme)
            
        if colour_scheme not in (0, 1, 2):
            self.colour_scheme = Set_Board_Colours.BROWN
            print("colour scheme not valid - set to default:",self.colour_scheme)
            return

        self.colour_scheme = colour_scheme

    def get_colour_scheme(self):
        return self.colour_scheme
        
    def get_square_colour(self):
        # darksquare / lightsquare 
        square_colours = (
          ( (205, 133,  63), (255, 222, 173) ),  # brown (default style)
          ( (131, 165, 210), (255, 255, 250) ),  # blue (droidfish style)
          ( (112, 160, 104), (200, 192, 96)  )   # green (xboard style)
        )
        return square_colours[self.colour_scheme]

    def show_pieces_dialog(self):
        pass

    def set_border_colour(self, cr, a): 
           image = self.wood1
           cr.set_source_surface(image, 0, 0)
           cairo.Pattern.set_extend(cr.get_source(), cairo.EXTEND_REPEAT)
           cr.rectangle(0, 0 , a.width, a.height)
           cr.fill()

    def show_dialog(self, gtkaction):
        dialog = Gtk.Dialog(
            _("Select Colour Scheme"), gv.gui.get_window(), 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        rb1 = Gtk.RadioButton.new_with_label(None, "Brown")
        dialog.vbox.pack_start(rb1, False, True, 5)
        rb2 = Gtk.RadioButton.new_with_label_from_widget(rb1, "Blue")
        dialog.vbox.pack_start(rb2, False, True, 5)
        rb3 = Gtk.RadioButton.new_with_label_from_widget(rb1, "Green")
        dialog.vbox.pack_start(rb3, False, True, 5)
        dialog.show_all()
        dialog.set_default_response(Gtk.ResponseType.OK)
        if self.colour_scheme == 0:
            rb1.set_active(True)
        elif self.colour_scheme == 1:
            rb2.set_active(True)
        elif self.colour_scheme == 2:
            rb3.set_active(True)
        else:
            rb1.set_active()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            if rb1.get_active():
                self.colour_scheme = 0
            elif rb2.get_active():
                self.colour_scheme = 1
            elif rb3.get_active():
                self.colour_scheme = 2
        dialog.destroy()
        return

    def apply_colour_settings(self):
        if gv.verbose:
            print("set_board_colours - apply_colour_settings")
        gv.gui.set_colours()
