# IMPORTS
import pyxel, random, math

# VARS

def circular(n, min, max):
    """
    Loop a given n number until it's in the inclusive interval. Return calibrated number.
    """
    d = max - min + 1
    while n < min:
        n += d
    while n > max:
        n -= d

    return n

def border(n, min=None, max=None):
    """
    Restrict a given number n in a "border" inclusive interval. Returns calibrated number.
    """
    if min is not None and n < min:
        n = min
    elif max is not None and n > max:
        n = max

    return n

def strr(r):
    """
    Stringify from int and round
    """
    return lambda i : str(round(i, int(r)))

str2 = strr(2)
str1 = strr(1)

"""
# TESTS - Restrict to
n = 5; min = 0; max = 10 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
n = -1; min = 0; max = 10 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
n = 11; min = 0; max = 10 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
n = 4; min = 1; max = 3 ;nc = restrict_to(n, min, max)
print(n, min, max, nc)
"""

class Game:
    def __init__(self, title, x=256, y=256, fps=30, name='', size=8, vx=4, spf=2, pdrag=0, borders='hard'):
        # Init game board
        self.xx = x     ### X maX
        self.yx = y     ### Y maX
        self.xn = 0     ### X miN
        self.yn = 0     ### Y miN
        self.fps = fps
        self.title = title
        self.timer = 0          ### DEPREC - Better use pyxel.frame_count
        self.shots_tot = 0
        self.borders = borders

        pyxel.init(self.xx, self.yx, title=self.title, fps=self.fps)

        # Init player
        self.xmov = 0
        self.ymov = 0
        self.vais = Player(self, name=name, size=size, vx=vx, spf=spf, drag=pdrag)

        # Init shot list
        self.shots_l = []

        # Launch the game, each frames per second
        print(f"GAME - Initialized {self.title} with x length = {self.xx}, y length = {self.yx} at {self.fps}fps")
        pyxel.run(self.update, self.draw)

    def __str__(self):
        return f"GAME - Running {self.title} with x length = {self.xx}, y length = {self.yx} at {self.fps}fps"

    def txt_main(self):
        self.tx = 10
        self.ty = 10
        self.tcol = 1
        self.txts_main = ["# Pyxel Game - title: " + self.title + "; borders=" + self.borders + ", fps=" + str(self.fps),
                          "size: x=" + str(self.xx) + ", y=" + str(self.yx),
                          "time: frames=" + str(pyxel.frame_count) + ", secs=" + str(round(pyxel.frame_count / self.fps, 1)),
                          "player: " + self.vais.name,
                          "pos: x=" + str(int(self.vais.x)) + ", y=" + str(int(self.vais.y)),
                          "stats: size=" + str(self.vais.size) + ", spf=" + str(self.vais.spf),
                          "velocity: absolute=" + str2(self.vais.absV) + ", max=" + str(self.vais.vx),
                          "accel: linear-m=" + str2(self.vais.m) + ", drag=" + str2(self.vais.drag),
                          "cardinal-v: y=" + str1(self.vais.cardV[0]) + ", x=" + str1(self.vais.cardV[1]) + ", -y=" + str1(self.vais.cardV[2]) + ", -x=" + str1(self.vais.cardV[3]),
                          "shots: active=" + str(len(self.shots_l)) + ", total=" + str(self.shots_tot), # "per-sec=" + str(round(len(self.shots_l) / (self.timer / self.fps), 1))
                          "---"]

        for txt in self.txts_main:
            pyxel.text(self.tx, self.ty, txt, self.tcol)
            self.ty += 6

    def input_player(self):
        """
        User basic input
        """
        # Menus
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        # Move. TODO correct wall collision system
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.xmov = 1
        if pyxel.btn(pyxel.KEY_DOWN):
            self.ymov = 1
        if pyxel.btn(pyxel.KEY_LEFT):
            self.xmov = -1
        if pyxel.btn(pyxel.KEY_UP):
            self.ymov = -1
        # Shoot
        if pyxel.btn(pyxel.KEY_SPACE) and pyxel.frame_count % self.vais.spf == 0: ### Limit to 1 shot per 2 frame
            #print("DEBUG - Player shot")
            self.shots_tot += 1
            self.shots_l.append(Shot(self, self.vais.x + int(self.vais.size/2), self.vais.y - 6, w=2))

    def input_debug(self):
        """
        Debug user inputs
        """
        # Reset pos
        if pyxel.btn(pyxel.KEY_O):
            self.vais.x = self.xx/2 - self.vais.size/2
            self.vais.y = self.yx/2 - self.vais.size/2

        # Change velocity
        if pyxel.btn(pyxel.KEY_Z) and self.vais.v > 0:
            self.vais.v -= 1
        elif pyxel.btn(pyxel.KEY_X):
            self.vais.v += 1
        # Change size
        if pyxel.btn(pyxel.KEY_C) and self.vais.size > 0:
            self.vais.size -= 1
        elif pyxel.btn(pyxel.KEY_V) and self.vais.size < 256:
            self.vais.size += 1



    """
    UPDATER
    """
    def update(self):
        # Timer. DEPREC - use pyxel.frame_count
        self.timer += 1

        # Input controls
        self.input_player()
        # Debug controls
        self.input_debug()
        # Movement calc
        self.vais.move(self.xmov, self.ymov)
        self.xmov = 0
        self.ymov = 0
        # Shots
        for shot in self.shots_l:
            shot.move()

    """
    DRAWER
    """
    def draw(self):
        # Start fresh each time
        pyxel.cls(0)

        # Text
        self.txt_main()
        # Shots
        for shot in self.shots_l:
            shot.draw()
        # Ship, draw a rectangle
        self.vais.draw()


class Player:
    def __init__(self, game, name='', size=8, v=2, vx=4, spf=2, drag=0):
        self.GAME = game
        self.x = (self.GAME.xx + size) / 2
        self.y = (self.GAME.yx + size) / 2
        self.name = name
        self.size = size
        self.v = v                  ### DEPREC - Actual velocity
        self.vx = vx                ### MaX accelerated Velocity
        self.xshift = 0
        self.yshift = 0
        # self.acct = 0             ### Timer in frames since last x movement
        # self.accty = 0            ### Timer in frames since last y movement
        self.spf = spf              ### Shot per frame
        self.cardV = [0, 0, 0, 0]   ### Mean of the 4 accel vector i, j, -i, -j clockwise
        self.m = 0.05               ### Linear factor, aka thruster power
        self.drag = drag

    def move(self, x, y):
        """
        Shift the vessel in the direction of x and y normalized vector {-1, 0, 1} time the velocity
        """
        """
        # Inertia (basic: omnidirectional fn); increase linear
        self.m = 0.05
        if (x != 0 or y != 0) and self.v <= self.vx:
            self.v += self.m
        elif self.v > 0:
            self.v -= self.m
        else:
            self.v = 0
        """
        # Inertia (cardinal); linear
        ## Increase (thruster on)
        self.cardV[0] += y * self.m
        self.cardV[1] += x * self.m
        self.cardV[2] -= y * self.m
        self.cardV[3] -= x * self.m
        ## Drag
        if self.drag > 0:
            self.cardV[0] -= self.m * self.drag
            self.cardV[1] -= self.m * self.drag
            self.cardV[2] -= self.m * self.drag
            self.cardV[3] -= self.m * self.drag

        ## Limit
        self.v = border(self.v, 0, self.vx)

        ## Final shift
        self.xshift = border(self.cardV[1] - self.cardV[3], min=-self.vx, max=self.vx)
        self.yshift = border(self.cardV[0] - self.cardV[2], min=-self.vx, max=self.vx)

        # Move
        self.absV = math.sqrt(self.xshift ** 2 + self.yshift ** 2)
        self.x += self.xshift
        self.y += self.yshift
        ## Check borders
        if self.GAME.borders == 'tor':
            self.cardV[0] = circular(self.cardV[0], 0, self.GAME.yx)
            self.cardV[1] = circular(self.cardV[1], 0, self.GAME.xx)
            self.cardV[2] = circular(self.cardV[2], 0, self.GAME.yx)
            self.cardV[3] = circular(self.cardV[3], 0, self.GAME.xx)
        else:
            self.cardV[0] = border(self.cardV[0], 0, self.GAME.yx)
            self.cardV[1] = border(self.cardV[1], 0, self.GAME.xx)
            self.cardV[2] = border(self.cardV[2], 0, self.GAME.yx)
            self.cardV[3] = border(self.cardV[3], 0, self.GAME.xx)

    def draw(self):
        pyxel.rect(self.x, self.y, self.size, self.size, 4)

class Shot:

    def __init__(self, game, x, y, w=2, h=8, v=2, team='WIP'):
        self.x = x
        self.y = y
        self.w = w          ### Width
        self.h = h          ### Height
        self.v = v          ### Velocity
        self.GAME = game    ### Actual gameboard
        # print("SHOT - Shot created; game recorded", self.GAME)

    def __str__(self):
        return f"SHOT - x={self.x}, y={self.y}, w={self.w}, h={self.h}, v={self.v}"

    def move(self):
        ## Here only one dir, up
        self.y -= self.v
        if self.y < self.GAME.yn - self.h + 1:
            self.GAME.shots_l.remove(self)
            # print("SHOTS - Shot deleted (out of bounds). List now:", self.GAME.shots_l)

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 10)


# EXEC

print("GAME - Started")
GAME = Game('Game1', 256, 256, name='Detroix23', pdrag=0.1, borders='hard')
print("GAME - Finished")