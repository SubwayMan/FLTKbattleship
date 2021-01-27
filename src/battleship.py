from fltk import *
import os
import socket

class tile(Fl_Button):

    def __init__(self, x, y, w, h):
        Fl_Button.__init__(self, x, y, w, h)
        self.is_ship = False
        self.revealed = False
class shipgrid(Fl_Group):
    """Class that contains each ship and handles events regarding them."""
    def __init__(self, x, y, sl, r, c):
        Fl_Group.__init__(self, x, y, c*sl, r*sl)
        self.tiles = []
        self.mode = "insert"

        for row in range(r):
            gx = []
            for col in range(c):
                a = Fl_Button(x+(row*sl), y+(col*sl), sl, sl)
                a.color(FL_BLUE)
                a.callback(self.but_cb)
                print(a.takesevents())
                gx.append(a)
            self.tiles.append(gx)

    def but_cb(self, w):
        w.color(FL_RED)

class Game(Fl_Double_Window):
    """Class that controls general game management."""
    def __init__(self, w, h):
        
        Fl_Double_Window.__init__(self, w, h, "Battleship")
        self.gridb = shipgrid(460, 20, 40, 10, 10)
        self.grida = shipgrid(20, 20, 40, 10, 10)
        self.show()
        Fl.run()

a = Game(880, 440)

