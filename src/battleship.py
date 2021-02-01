from fltk import *
import os
import socket

#INSTRUCTIONS
#Start hosting with the menu bar
#Connect to the address outputted in console
#Use shift to switch ship orientation
class Tile(Fl_Button):
    """Button class that also stores position in grid."""
    def __init__(self, x, y, w, h, r, c) -> None:
        """Constructor - normal button constructor, with grid coords."""
        Fl_Button.__init__(self, x, y, w, h)
        self.r = r
        self.c = c
        #Store if ship or already revealed for external use
        self.isship = False
        self.revealed = False
            
class Ship():
    """helper class that detects if sunk and stores ship coords."""
    def __init__(self, size, l) -> None:
        """Constructor - size and list of coords"""
        self.size = size
        #store hits
        self.hits = 0
        self.posit = l

    def reduce(self) -> bool:
        """Adds to hits and returns true if sank."""
        self.hits += 1
        if self.hits == self.size:
            return True
        return False
        

class shipgrid(Fl_Group):
    """Main grid class that controls ship placing, event handling, etc."""

    def __init__(self, x, y, sl, r, c, gamelistener) -> None:
        """Constructor - takes x&y position coords, a sidelength for a tile, number of rows
        and columns, and a main class for handling network events."""
        Fl_Group.__init__(self, x, y, c*sl, r*sl)
        #Store tiles, sidelength, ships, shipsizes
        self.tiles = []
        self.sl = sl
        self.ships = []
        self.shipsizes = [2, 3, 3, 4, 5]
        #Dictionary that keeps coords with ships at them and the ship they point to
        self.ship_to_coords = {}
        #Position in the shipsizes list used during creation
        self.spos = 0
        #grid mode and ship orientation
        self.mode = "NC"
        self.orient = "H"
        #store main class
        self.gamel = gamelistener
        self.begin()

        #create tiles
        for row in range(r):
            gr = []
            for col in range(c):
                a = Tile(x+(col*sl), y+(row*sl), sl, sl, row, col)
                a.color(FL_BLUE)

                a.callback(self.click_cb)
                gr.append(a)
            self.tiles.append(gr)
        self.end()
    
    def handle(self, e) -> int:
        """Handle method, mostly ship placing functionality."""
        a = super().handle(e)
        #switch ship orientation
        if e == FL_KEYUP:
            if self.mode == "set":
                if Fl.event_key() == FL_Shift_L:
                    self.orient = ("W" if self.orient == "H" else "H")
                    return 1
        #ship preview when placing
        if e == FL_MOVE:
            #reset any tiles from last hover
            for grow in self.tiles:
                for gt in grow:
                    if not gt.isship and not gt.revealed:
                        gt.color(FL_BLUE)
            #relative x and y coords
            mx, my = (Fl.event_x()-self.x())//self.sl, (Fl.event_y()-self.y())//self.sl
            #check mode
            if self.mode == "set":
                #horizontal ship
                if self.orient=="H":
                    for i in range(self.shipsizes[self.spos]):
                        if i+mx>9:
                            break
                        t = self.tiles[my][mx+i]
                        if t.isship:
                            break
                        t.color(fl_rgb_color(255, 123, 0))
                else:
                    #vertical ship
                    for i in range(self.shipsizes[self.spos]):
                        if i+my>9:
                            break
                        t = self.tiles[my+i][mx]
                        if t.isship:
                            break
                        t.color(fl_rgb_color(255, 123, 0))
                self.redraw()
                return 1

        return a
    
   
    def click_cb(self, w) -> None:
        """Event handler for each tile."""
        #do nothing if revealed
        if w.revealed:
            return None
        #insert ship
        if self.mode == "set":
            self.ins_ship(w.r, w.c)
        #if is turn and mode is guess, send guess
        elif self.mode == "guess" and self.gamel.turn:
            self.gamel.gate_t(w.r, w.c)
    
    def reveal(self, r, c) -> bool:
        """Guess method."""

        self.tiles[r][c].revealed = True
        if (r, c) in self.ship_to_coords:
 
            self.tiles[r][c].color(FL_RED)
            #get ship and check for sinking
            jship = self.ship_to_coords[(r, c)]
            if jship.reduce(): 
                for row, col in jship.posit:
                    self.tiles[row][col].color(FL_BLACK)
                self.redraw()
                return jship.posit
            self.redraw()
            return True
        else:
            #incorrect guess
            self.tiles[r][c].color(fl_rgb_color(3, 252, 227))
            self.redraw()
            return False
   
    def disp(self, r, c, v) -> None:
        """Reveal method for client grid from incoming event."""
        if v=="N":
            self.tiles[r][c].color(fl_rgb_color(3, 252, 227))
        elif v=="S":
            self.tiles[r][c].color(FL_BLACK)
        else:
            self.tiles[r][c].color(FL_RED)
        self.redraw()
        self.tiles[r][c].revealed = True

    def ins_ship(self, row, col) -> bool:
        """Method that inserts ship, returns validity of ship placement."""
        size = self.shipsizes[self.spos]
        if self.orient == "H":
            if col+size>10: return False
            tiles = [(row, col+f) for f in range(size)]
        else: 
            if row+size>10: return False
            tiles = [(row+f, col) for f in range(size)]

        if any(a in self.ship_to_coords for a in tiles):
            return False
        
        nship = Ship(size, tiles)
        for j in tiles:
            self.ship_to_coords[j] = nship
            self.tiles[j[0]][j[1]].color(FL_YELLOW)
            self.tiles[j[0]][j[1]].isship = True
        self.spos += 1
        if self.spos >= len(self.shipsizes):
            #change mode if all ships placed
            self.mode = "WAIT"
            self.gamel.aready = True
            self.gamel.conn.sendall("R".encode())
            self.gamel.ready()
        self.redraw()
        return True

class Game(Fl_Double_Window):
    """Class that controls general game management and networking."""
    def __init__(self, w, h):
        """Constructor, args: width and height"""
        Fl_Double_Window.__init__(self, 20, 20, w, h, "Battleship")
        self.grida = shipgrid(20, 30, 40, 10, 10, self)
        self.gridb = shipgrid(460, 30, 40, 10, 10, self)
        self.mb = Fl_Menu_Bar(0, 0, self.w(), 20)
        self.mb.add("Connect/Host", 0, self.host)
        self.mb.add("Connect/Remote", 0, self.clientcon)
        self.conn = None
        self.gridb.mode = "disp"
        self.hits = 0
        self.guesses = 0
        self.console = Fl_Multi_Browser(20, 450, 840, 140)
        self.show()
        self.hold = None
        Fl.run()

    def host(self, w=None) -> None:
        """Method to start hosting locally."""
        self.so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.so.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.port = 7282
        self.so.bind(("0.0.0.0", self.port))
        self.so.listen()
        fdl = self.so.fileno()
        Fl.add_fd(fdl, self.acc_conn)
        self.console.add(f"hosting with address {socket.gethostbyname(socket.gethostname())}")

    def acc_conn(self, f):
        "For hosting when receiving incoming connection."
        self.conn, raddr = self.so.accept()
        self.fd = self.conn.fileno()
        Fl.add_fd(self.fd, self.recpacket)
        self.console.add(f"Connected to {raddr}")
        self.turn = True
        self.begingame()

    def hide(self):
        """extending hide to assure connection closing."""
        super().hide()
        try:
            self.conn.close()
        except:
            pass

    def clientcon(self, w=None):
        """callback for entering ip and connecting."""
        if self.conn:
            fl_alert("Connection already exists!")
            return None
        addr = fl_input("Enter host IP", "127.0.0.1")
        res = self.connto(addr)
        if not res:
            self.console.add("Invalid connection!")

    def connto(self, addr):
        """For client->server connection via tcp."""
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((addr, 7282))
            self.fd = self.conn.fileno()
        except (socket.gaierror, TimeoutError, ConnectionRefusedError):
            self.conn = None
            return False

        Fl.add_fd(self.fd, self.recpacket)
        self.turn = False
        self.console.add(f"Connected to remote host {addr}.")
        self.begingame()
        return True

    def gate_t(self, row, col):
        """Method that sends a guess to other player."""
        n = "G"+str(row)+" "+str(col)
        self.hold = (row, col)
        self.conn.sendall(n.encode())
        self.turn = False

    def recpacket(self, f):
        """General receive method over network."""
        a = self.conn.recv(1024)
        
        #remote close
        if a==b"":
            self.console.add("Connection closed.")
            self.conn.close()
            self.conn = None
            Fl.remove_fd(f)
        else:
            n = a.decode()
            #is a guess result
            if n[0] in "YN":
                self.guesses += 1
                if n[0] == "Y": self.hits += 1 
                if len(n)>2:
                    coords = [list(map(int, x.split())) for x in n[1:].split(",")]
                    for row, col in coords:
                        self.gridb.disp(row, col, "S")
                    self.console.add(f"ENEMY SHIP SUNK on row {self.hold[0]}, column {self.hold[1]}")
                    if self.hits==17:
                        self.endgame("W")
                        self.conn.sendall("L".encode())
                    return None
                self.gridb.disp(self.hold[0], self.hold[1], n)
                res = ("MISS" if a.decode()=="N" else "HIT")
                
                self.console.add(f"{res} on row {self.hold[0]}, column {self.hold[1]}")
                return None
            #is an incoming guess
            elif n[0] == "G":
                self.turn = True
                rg, cg = map(int, n[1:].split())
                ans = self.grida.reveal(rg, cg)
                if ans:
                    if isinstance(ans, list):
                        sunksh = ",".join(str(f[0])+" "+str(f[1]) for f in ans)
                        self.conn.sendall(("Y"+sunksh).encode())
                        self.console.add(f"SHIP SANK on row {rg}, column {cg}")
                    else: 
                        self.conn.sendall("Y".encode())
                        self.console.add(f"ENEMY HIT on row {rg}, column {cg}")
                else:
                    self.console.add(f"ENEMY MISS on row {rg}, column {cg}")
                    self.conn.sendall("N".encode())
                return None
            #is a notification of ready status
            elif n[0] == "R":
                self.bready = True
                self.ready()
                return None
            #Is an indication of game loss
            elif n[0] == "L":
                self.endgame("L")
                return None
            self.console.add("Data received!")

    def endgame(self, cond):
        """End the game."""
        self.grida.mode = "inac"
        self.gridb.mode = "inac"
        if cond == "W":
            fl_alert("Congratulations you won!")
            self.console.add(f"Game won with {self.guesses} guesses.")
        else:
            fl_alert("Sorry, you lost.")
            self.console.add(f"Enemy won.")

    def begingame(self):
        """Start the game."""
        self.grida.mode = "set"
        self.aready = False
        self.bready = False

    def ready(self):
        """Verify if both players have ships set."""
        if self.aready and self.bready:
            self.grida.mode = "DISP"
            self.gridb.mode = "guess"
            if self.turn:
                self.console.add("Game starting - your turn!")
            else:
                self.console.add("Game starting - enemy's turn!")

a = Game(880, 610)

