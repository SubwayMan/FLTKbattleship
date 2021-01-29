from fltk import *
import os
import socket

class Tile(Fl_Button):
    def __init__(self, x, y, w, h, r, c):
        Fl_Button.__init__(self, x, y, w, h)
        self.r = r
        self.c = c

class Ship():
    def __init__(self, size, r, c, orient):
        self.size = size
        self.r = r
        serlf.c = c
        self.hits = 0
        if orient == "H":
            self.tiles = [(r, c+f) for f in range(size)]
        else:
            self.tiles = [(r, c+f) for f in range(size)]

    def reduce(self):
        self.hits += 1
        if self.hits == self.size:
            return True
        return False
        
class shipgrid(Fl_Group):
    """Class that contains each ship and handles events regarding them."""
    def __init__(self, x, y, sl, r, c):
        Fl_Group.__init__(self, x, y, c*sl, r*sl)
        self.tiles = []
        self.ships = []
        self.shipsizes = [2, 3, 3, 4, 5]
        self.spos = 0
        self.mode = "set"
        self.orient = "H"
        self.begin()
        for row in range(r):
            gr = []
            for col in range(c):
                a = Tile(x+(row*sl), y+(col*sl), sl, sl)
                a.color(FL_BLUE)
                a.callback(self.click_cb)
                gr.append(a)
            self.tiles.append(gr)
        self.end()

    def click_cb(self, w):
        """Event handler for the grid."""
        if self.mode == "set":
           pass 
class Game(Fl_Double_Window):
    """Class that controls general game management."""
    def __init__(self, w, h):
        
        Fl_Double_Window.__init__(self, w, h, "Battleship")
        self.gridb = shipgrid(460, 20, 40, 10, 10)
        self.grida = shipgrid(20, 20, 40, 10, 10)
        self.show()
        Fl.run()

a = Game(880, 440)

