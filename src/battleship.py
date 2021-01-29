from fltk import *
import os
import socket

class Tile(Fl_Button):
    def __init__(self, x, y, w, h, r, c):
        Fl_Button.__init__(self, x, y, w, h)
        self.r = r
        self.c = c

class Ship():
    def __init__(self, size, l):
        self.size = size
        self.hits = 0
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
        self.ship_to_coords = {}
        self.spos = 0
        self.mode = "set"
        self.orient = "H"
        self.begin()
        for row in range(r):
            gr = []
            for col in range(c):
                a = Tile(x+(row*sl), y+(col*sl), sl, sl, row, col)
                a.color(FL_BLUE)
                a.callback(self.click_cb)
                gr.append(a)
            self.tiles.append(gr)
        self.end()
    
    def handle(self, e):
        a = super().handle(e)
        if e == FL_PUSH:
            if Fl.event_button() == FL_RIGHT_MOUSE:
                self.orient = ("W" if self.orient == "H" else "H")
                return 1
        return a
    def click_cb(self, w):
        """Event handler for the grid."""
        if self.mode == "set":
            self.ins_ship(w.r, w.c)
        else:
            pass

    def ins_ship(self, row, col):
        size = self.shipsizes[self.spos]
        if self.orient == "H":
            if row+size>10: return False
            tiles = [(row+f, col) for f in range(size)]
        else: 
            if col+size>10: return False
            tiles = [(row, col+f) for f in range(size)]

        if any(a in self.ship_to_coords for a in tiles):
            return False
        
        nship = Ship(size, tiles)
        for j in tiles:
            self.ship_to_coords[j] = nship
            self.tiles[j[0]][j[1]].color(FL_RED)
        self.spos += 1
        if self.spos >= len(self.shipsizes):
            self.mode = "guess"
        self.redraw()
        return True

class Game(Fl_Double_Window):
    """Class that controls general game management."""
    def __init__(self, w, h):
        
        Fl_Double_Window.__init__(self, w, h, "Battleship")
        self.gridb = shipgrid(460, 20, 40, 10, 10)
        self.grida = shipgrid(20, 20, 40, 10, 10)
        self.show()
        Fl.run()

a = Game(880, 440)

