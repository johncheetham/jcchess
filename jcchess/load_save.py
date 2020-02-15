#
#   load_save.py
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
from gi.repository import GLib
from gi.repository import Gtk
import os
from datetime import date
from . import gv
from . import move_list
from . import comments
from . import gamelist
import chess.pgn
from .constants import WHITE, BLACK,  VERSION,  NAME


class Load_Save:

    def __init__(self):
        self.move_list = move_list.get_ref()
        self.comments = comments.get_ref()
        self.gamelist = gamelist.get_ref()

    # Load game from a previously saved game
    def load_game(self, b):
        dialog = Gtk.FileChooserDialog(
            _("Load.."), gv.gui.get_window(), Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        #dialog.set_current_folder(os.path.expanduser("~"))
        dialog.set_current_folder(gv.lastdir)
        filter = Gtk.FileFilter()
        filter.set_name("pgn files")
        filter.add_pattern("*.pgn")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        response = dialog.run()
        if response != Gtk.ResponseType.OK:
            dialog.destroy()
            return

        fname = dialog.get_filename()
        gv.lastdir = os.path.dirname(fname)
        if gv.verbose == True:       
            print ("opening: " + os.path.dirname(fname))
        gv.gui.window.set_title(NAME + " " + VERSION + "  " + os.path.basename(fname))
        dialog.destroy()

        if fname.endswith(".pgn"):
            self.get_header_from_file(fname)
            #entries from malformatted files would break the GUI of the program
            if gv.show_header == True:
                GLib.idle_add(gv.gui.header_lblsente.set_text, gv.sente[:50])
                #print(gv.sente)
                GLib.idle_add(gv.gui.header_lblgote.set_text, gv.gote[:50])
                #print(gv.gote)
                GLib.idle_add(gv.gui.header_lblevent.set_text, gv.event[:50])
                #print(gv.event)
                GLib.idle_add(gv.gui.header_lbldate.set_text, gv.gamedate[:50])
                #print(gv.gamedate)

            gamecnt = 0
            self.file_position = []
            self.gamelist.clear()
            
            # get headers and offsets of games
            f = open(fname)
            self.fname = fname
            for offset, headers in chess.pgn.scan_headers(f):
                gamecnt += 1
                self.gamelist.addgame(gamecnt, headers)
                self.file_position.append(offset)
            f.close()

            # No games in file
            if gamecnt == 0:
                gv.gui.info_box("No games in file")
                return

            # single game file - Load the game
            if gamecnt == 1:
                self.load_game_from_multigame_file(1)
                return

            # multi game file - Display the Game List so user can select a game
            self.gamelist.show_gamelist_window()

    # called from gamelist.py to load the game selected from the gamelist
    # of a multigame file
    def load_game_from_multigame_file(self, gameno):
        f = open(self.fname)
        f.seek(self.file_position[gameno - 1])
        game = chess.pgn.read_game(f)
        f.close()
        self.load_game_pgn(game)

    def load_game_pgn(self, game):
        stm = WHITE
        moveno = 0
        movelist = []
        redolist = []
        lastmove = ""
        startpos = "startpos"
        # if there is a FEN use that as board start position 
        # otherwise use standard start position
        try:
            fen = game.headers["FEN"]
        except KeyError:
            fen = "std"
        if gv.verbose:
            print("game=",game)
            print("fen=",fen)
        gv.board.init_board(fen)
        node = game
        while not node.is_end():
            next_node = node.variation(0)
            stm = stm ^ 1 
            move = node.board().san(next_node.move)
            if gv.verbose:
                print("move=", move)
                print("type=",type(move))
            move = gv.board.parse_san(move)
            if gv.verbose:
                print("move=", move)
                print("type=",type(move))
            gv.board.add_move(move)
            smove = str(move)                
            movelist.append(smove)
            lastmove = smove
            
            # add comment for this move if present
            if node.comment != "":
                self.comments.set_comment(moveno, node.comment)
                        
            moveno += 1
            if gv.verbose:
                gv.board.print_board()
            node = next_node
            
        gv.ucib.set_newgame()                    
        gv.uciw.set_newgame()
        gv.gui.set_status_bar_msg("game loaded")
        #self.gameover = False

        gv.jcchess.set_movelist(movelist)
        gv.jcchess.set_redolist(redolist)
        gv.jcchess.set_startpos(fen)
        gv.jcchess.set_lastmove(lastmove)

        gv.board.update()

        # update move list in move list window
        self.move_list.update()
        stm = gv.jcchess.get_side_to_move()
        gv.jcchess.set_side_to_move(stm)
        gv.gui.set_side_to_move(stm)

        gv.tc.reset_clock()

        return 0

    #loads filename from 1st argument in commandline
    def load_game_parm(self,fname):
        try:
                fp = open(fname)
        except  :
                gv.gui.info_box("Error  loading game - file not found")
                return
        fp.close()
        gv.gui.window.set_title(NAME + " " + VERSION + "  " + os.path.basename(fname))
        
        if fname.endswith(".psn"):
            self.get_header_from_file(fname)
            if gv.show_header == True:
                GLib.idle_add(gv.gui.header_lblsente.set_text, gv.sente[:50])
                GLib.idle_add(gv.gui.header_lblgote.set_text, gv.gote[:50])
                GLib.idle_add(gv.gui.header_lblevent.set_text, gv.event[:50])
                GLib.idle_add(gv.gui.header_lbldate.set_text, gv.gamedate[:50])
            self.psn.load_game_psn(fname)
            return

    def get_header_from_file(self, fname):
        # sente,gote,event, date
        try:
                f = open(fname)
        except:
                gv.gui.info_box("Error  loading game-headers - file not found")
                
                return
        myList = []
        for line in f:
                myList.append(line)
        f.close()
        ff = False
        eventfound = False
        for line in myList:
                if line[0] == "[":
                        if line.find("Date") != -1:
                                gv.gamedate = line[6:-2]
                                #print("Date: ", gv.gamedate)
                                ff = True
                        if line.find("Event") !=-1:
                                gv.event = line[7:-2]
                                if gv.event=="" or gv.event=="##":
                                        gv.event="none"
                                #print(gv.event)
                                ff = True
                                eventfound = True
                               
                        if (line.find("Black")!=-1 or line.find("Sente")!=-1 ) and (line.find("SenteGrade")==-1) and (line.find("Black_grade")==-1):
                                        gv.sente =  line[8:-2] #"Sente:" +
                                        
                                        ff = True
                        if (line.find("White")!=-1 or line.find("Gote")!=-1) and (line.find("GoteGrade")==-1) and (line.find("White_grade")==-1):
                                gv.gote = line[7:-2]  #"Gote:" +
                                ff = True
        #if eventfound == False and myList[0][0] == "[":
         #       gv.event = myList[0][1:-1]              #educated guess
        #print("header from file:", gv.gamedate,  gv.gote,  gv.sente,  gv.event)
        if ff == True:
                # Header from file: mask in event removed
                if gv.event.find("##")!=-1:
                        gv.event = "no event"
                if gv.show_header == True:
                    GLib.idle_add( gv.gui.header_lbldate.set_text, gv.gamedate[:50])
                    GLib.idle_add( gv.gui.header_lblgote.set_text,  gv.gote[:50])
                    GLib.idle_add( gv.gui.header_lblsente.set_text, gv.sente[:50])
                    GLib.idle_add( gv.gui.header_lblevent.set_text, gv.event[:50])
        else:
                gv.event = "##"  # marks file without header
                
                
    # this routine is called from utils.py (when doing paste position)
    # and from gui.py (when ending an edit board session).
    def init_game(self, fen):
        gv.board.init_board(fen)
        startpos = fen
        #fenlst = fen.split()
        #if fenlst[1] == "b":
        #    if gv.verbose:
        #        print("setting stm to black")
        #    stm = BLACK
        #elif fenlst[1] == "w":
        #    stm = WHITE
        #else:
        #    stm = BLACK
        #engine.setplayer(stm)

        gv.ucib.set_newgame()
        gv.uciw.set_newgame()
        gv.gui.set_status_bar_msg(_("ready"))
        #self.gameover = False

        gv.jcchess.set_movelist([])
        gv.jcchess.set_redolist([])
        gv.jcchess.set_startpos(startpos)

        gv.board.update()

        # update move list in move list window
        self.move_list.update()

        stm = gv.jcchess.get_side_to_move()
        gv.jcchess.set_side_to_move(stm)
        gv.gui.set_side_to_move(stm)
        gv.jcchess.set_lastmove("")

        gv.tc.reset_clock()

    # called from utils.py as well as from this module
    def get_game(self):

        gamestr = ""
        startpos = gv.jcchess.get_startpos()
        # properties
        dat = str(date.today())
        dat = dat.replace("-", "/")

        zstr = '[Date "' + dat + '"]\n'
        gamestr += zstr

        zstr =  '[Sente: ' + gv.jcchess.get_player(BLACK).strip() + '"]\n'   
        gamestr += zstr

        zstr =  '[Gote: ' + gv.jcchess.get_player(WHITE).strip() + '"]\n' 
        gamestr += zstr

        # sfen
        if startpos == "startpos":
            zstr = '[SFEN "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP' \
                   '/1B5R1/LNSGKGSNL b - 1"]\n'
            gamestr += zstr
        else:
            zstr = '[SFEN "' + startpos + '"]\n'
            gamestr += zstr

        # add comment if present
        comment = self.comments.get_comment(0)
        if comment != "":
            gamestr = gamestr + "{\n" + comment + "\n}\n"

        # if the movelist is positioned part way through the game then
        # we must redo all moves so the full game will be saved
        redo_count = len(gv.jcchess.get_redolist())
        for i in range(0, redo_count):
            gv.jcchess.redo_move()

        # moves
        moveno = 1
        # ml = self.movelist
        mvstr = engine.getmovelist()

        # if we did any redo moves then undo them now to get things back
        # the way they were
        for i in range(0, redo_count):
            gv.jcchess.undo_move()

        if mvstr != "":
            mlst = mvstr.split(",")

            for m in mlst:

                (capture, ispromoted, move) = m.split(";")

                if move.find("*") == -1:
                    m1 = move[0:3]
                    m2 = move[3:]
                    move = m1 + capture + m2
                    if ispromoted == "+":
                        move = "+" + move
                zstr = str(moveno) + "." + move + "\n"
                gamestr += zstr
                # add comment for this move if present
                comment = self.comments.get_comment(moveno)
                if comment != "":
                    gamestr = gamestr + "{" + comment + "}\n"
                moveno += 1
        return (gamestr)

    # Save game to a file
    def save_game(self, b):

        dialog = Gtk.FileChooserDialog(
            _("Save.."), gv.gui.get_window(), Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_current_folder(gv.lastdir)

        filter = Gtk.FileFilter()
        filter.set_name("pgn files")
        filter.add_pattern("*.pgn")
        dialog.add_filter(filter)

        filter = Gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:

            startpos = gv.jcchess.get_startpos()

            #
            # filename must end with .pgn
            #
            filename = dialog.get_filename()
            gv.lastdir = os.path.dirname(filename)
            if gv.verbose == True:
                print("saving: " + gv.lastdir)
            gv.gui.window.set_title(NAME + " " + VERSION + "  " + os.path.basename(filename))
           
            if not filename.endswith('.pgn'):
                if dialog.get_filter().get_name() == "pgn files":
                    filename = filename + ".pgn" 

            # If file already exists then ask before overwriting
            if os.path.isfile(filename):
                resp = gv.gui.ok_cancel_box(
                    _("Warning - file already exists and will be replaced.\n"
                      "Press Cancel if you do not want to overwrite it."))
                if resp == Gtk.ResponseType.CANCEL:
                    dialog.destroy()
                    return
                    
            if filename.endswith(".pgn"):
                    
                game = gv.board.get_game()

                # add comments
                moveno = 0    
                node = game
                while not node.is_end():
                    next_node = node.variation(0)                                              
                    # add comment for this move if present
                    comment = self.comments.get_comment(moveno)
                    if comment != "":
                        node.comment = comment 
                    node = next_node
                    moveno += 1                
                   
                # write game to file                
                f = open(filename, "w",)
                print(game, file=f, end="\n\n")
                f.close()
                
            """
            if filename.endswith(".pgn"):
                # save in psn format
                gamestr = self.get_game()
                # we must get the last header read:
                gamelist = gamestr.splitlines(True) 
                #if gv.verbose == True:
                #print("Save psn:", gv.event,  gv.gamedate,  gv.sente,  gv.gote)
                if gv.event.find("##")==-1: 
                        #event not labelled with '##: 
                        #we must insert header from settings
                        #if gv.verbose == True:
                        #print( gv.event, "header rewritten")
                        gamelistnew = []
                        gamelistnew.append("[" + gv.event + "]\n")
                        gamelistnew.append("[Date: " + gv.gamedate+ "]\n")
                        gamelistnew.append("[Black:  " + gv.sente + "]\n")
                        gamelistnew.append("[White:  " + gv.gote + "]\n")
                        for item in gamelist[3:]:
                                gamelistnew.append(item)
                        gamestrnew =""
                        
                        for item in range(0, len(gamelistnew)):
                                gamestrnew = gamestrnew + str(gamelistnew[item])
                                
                        gamelistnew = ()
                        gamelist = ()
                        gamestr = gamestrnew
                
                f = open(filename, "w")
                f.write(gamestr)
                f.close()
            """
            
            gv.gui.set_status_bar_msg(_("game saved:  " + filename) + "  "+ VERSION)

        dialog.destroy()
