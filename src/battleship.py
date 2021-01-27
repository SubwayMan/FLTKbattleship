from fltk import *
import os
import socket

class shipgrid(Fl_Group):
    """Class that contains each ship and handles events regarding them."""
    def __init__(self, x, y, sl, r, c):
        Fl_Group.__init__(self, x, y, c*sl, r*sl)
        self.tiles = []

        for row in range(r):
            gx = []
            for col in range(c):
                a = Fl_Button(x+(row*sl), y+(col*sl), sl, sl)
                a.color(FL_BLUE)
                gx.append(a)
            self.tiles.append(gx)

class Game(Fl_Double_Window):
    """Class that controls general game management."""
    def __init__(self, w, h):
        
        Fl_Double_Window.__init__(self, w, h, "Battleship")
        self.grida = shipgrid(20, 20, 40, 10, 10)
        self.gridb = shipgrid(460, 20, 40, 10, 10)
        self.show()
        Fl.run()

a = Game(880, 440)

